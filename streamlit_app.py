from datetime import date, datetime, timedelta

import streamlit as st

from ai_ladders import ai_available, generate_ladder
from goals_library import GOAL_LIBRARY, get_goal_options
from storage import load_data, save_data

TIMELINE_PRESETS = {
    "2 weeks (sprint)": 14,
    "1 month": 30,
    "2 months": 60,
    "3 months": 90,
    "6 months": 180,
    "1 year (slow & steady)": 365,
    "Custom...": None,
}

st.set_page_config(page_title="Tiny Steps", page_icon="🌱", layout="centered")


if "data" not in st.session_state:
    st.session_state.data = load_data()


# ------------------------------------------------------------ pacing math ---

def goal_days(goal):
    start = date.fromisoformat(goal["start_date"])
    end = date.fromisoformat(goal["end_date"])
    total = max((end - start).days, 1)
    day_index = (date.today() - start).days  # 0-based; can exceed total after deadline
    return total, day_index


def levels_for(goal):
    """A goal's ladder: its own AI-generated one if present, else the library's."""
    return goal.get("custom_levels") or GOAL_LIBRARY[goal["category"]]["levels"]


MAX_OFFSET = 3  # how far your feedback can shift you from the timeline's pace


def level_offset(goal):
    """Persistent adjustment from 'too easy' / 'too hard' feedback."""
    try:
        return max(-MAX_OFFSET, min(MAX_OFFSET, int(goal.get("level_offset", 0))))
    except (TypeError, ValueError):
        return 0


def current_level_index(goal):
    """Map today onto the ladder, then apply the user's own difficulty feedback.

    Short timelines climb fast, long ones slow; level_offset lets someone who
    finds the steps too easy or too hard move the whole ladder with them.
    """
    levels = levels_for(goal)
    total, day_index = goal_days(goal)
    day_index = min(max(day_index, 0), total - 1)
    paced = day_index * len(levels) // total
    return max(0, min(len(levels) - 1, paced + level_offset(goal)))


def task_for_day(goal, level_offset=0):
    """Deterministic daily task: same task all day, rotates variants day to day."""
    levels = levels_for(goal)
    lvl = max(0, current_level_index(goal) + level_offset)
    lvl = min(lvl, len(levels) - 1)
    level = levels[lvl]
    _, day_index = goal_days(goal)
    variant = level["tasks"][max(day_index, 0) % len(level["tasks"])]
    return lvl, level["title"], variant


def pace_label(total_days, num_levels):
    days_per_level = total_days / num_levels
    if days_per_level <= 4:
        return "🚀 Accelerated", f"~{max(1, round(days_per_level))} day(s) per level — bigger steps, faster climb"
    if days_per_level <= 12:
        return "⚡ Steady climb", f"~{round(days_per_level)} days per level — solid daily progress"
    return "🌿 Slow & gradual", f"~{round(days_per_level)} days per level — tiny baby steps with lots of practice"


def compute_streak(goal):
    """Return (streak, shields_available).

    Streak counts back from today (or yesterday if today isn't done yet).
    Shields protect streaks: every 7 completed tasks earns one, and each can
    auto-cover a single missed day. Two missed days in a row always break.
    """
    done = set(goal.get("completed_dates", []))
    shields_earned = len(done) // 7
    used = 0
    day = date.today()
    if day.isoformat() not in done:
        day -= timedelta(days=1)
    streak = 0
    while True:
        if day.isoformat() in done:
            streak += 1
        elif used < shields_earned and (day - timedelta(days=1)).isoformat() in done:
            used += 1
        else:
            break
        day -= timedelta(days=1)
    return streak, max(shields_earned - used, 0)


# ------------------------------------------------------ milestones & stats ---

MILESTONES = [
    (1, "🌱", "First step"),
    (3, "🌿", "Three days in"),
    (7, "⭐", "One week"),
    (14, "🔥", "Two weeks"),
    (30, "💪", "Thirty tasks"),
    (50, "🏅", "Fifty strong"),
    (75, "🚀", "Seventy-five"),
    (100, "💎", "One hundred"),
    (150, "👑", "One-fifty"),
    (200, "🏆", "Two hundred"),
]


def milestones_for(done_count):
    """Return (earned, next_one). next_one is None once every badge is earned."""
    earned = [m for m in MILESTONES if done_count >= m[0]]
    upcoming = next((m for m in MILESTONES if done_count < m[0]), None)
    return earned, upcoming


def heatmap_rows(goal, weeks=12):
    """Week rows of 🟩/⬜/·  for the last `weeks` weeks, Monday-aligned."""
    done = set(goal.get("completed_dates", []))
    start = date.fromisoformat(goal["start_date"])
    today = date.today()
    # End on the Sunday of this week so columns line up under weekday headers.
    end = today + timedelta(days=6 - today.weekday())
    first = end - timedelta(days=weeks * 7 - 1)
    rows = []
    day = first
    while day <= end:
        cells = []
        for _ in range(7):
            if day < start or day > today:
                cells.append("·")  # outside the journey
            elif day.isoformat() in done:
                cells.append("🟩")
            else:
                cells.append("⬜")
            day += timedelta(days=1)
        rows.append("".join(cells))
    return rows


# ---------------------------------------------------------------- add goal ---

def render_add_goal(first_goal=False):
    if first_goal:
        st.markdown(
            "Pick something you want to get better at. Every day you'll get **one small task** — "
            "the size of the steps depends on how much time you give yourself."
        )
    options = get_goal_options()
    labels = [label for _, label in options]
    choice = st.selectbox("What do you want to improve?", labels, key="new_goal_cat")
    category = options[labels.index(choice)][0]

    custom_name = None
    if category == "custom":
        custom_name = st.text_input(
            "Name your goal", placeholder="e.g. Learn guitar, wake up earlier, save money..."
        )
        if ai_available():
            st.caption("✨ AI will build a personalized 8-level plan just for this goal.")
    else:
        st.caption(GOAL_LIBRARY[category]["description"])

    st.markdown("**How long do you want to give yourself?**")
    st.caption(
        "This matters: 2 months means bigger steps and a faster climb. "
        "A year means slower, gentler baby steps with more practice at each stage."
    )
    timeline = st.selectbox("Timeline", list(TIMELINE_PRESETS.keys()), index=2, key="new_goal_tl")
    days = TIMELINE_PRESETS[timeline]
    if days is None:
        end = st.date_input(
            "Target date",
            value=date.today() + timedelta(days=60),
            min_value=date.today() + timedelta(days=7),
            key="new_goal_date",
        )
        days = (end - date.today()).days

    num_levels = len(GOAL_LIBRARY[category]["levels"])
    pace, pace_detail = pace_label(days, num_levels)
    st.info(f"**{pace}** — {days} days across {num_levels} levels. {pace_detail}.")

    if st.button("Start this journey 🌱", type="primary", use_container_width=True):
        if category == "custom" and not (custom_name or "").strip():
            st.error("Give your custom goal a name first.")
            return
        goal = {
            "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
            "category": category,
            "name": (custom_name.strip() if custom_name else GOAL_LIBRARY[category]["name"]),
            "start_date": date.today().isoformat(),
            "end_date": (date.today() + timedelta(days=days)).isoformat(),
            "completed_dates": [],
        }
        if category == "custom" and ai_available():
            with st.spinner("✨ Building your personalized plan..."):
                custom_levels = generate_ladder(goal["name"], days)
            if custom_levels:
                goal["custom_levels"] = custom_levels
            else:
                st.info("AI plan wasn't available right now — using the proven generic ladder instead.")
        st.session_state.data["goals"].append(goal)
        save_data(st.session_state.data)
        st.session_state.pop("adding_goal", None)
        st.rerun()


# --------------------------------------------------------------- goal view ---

def render_feedback(goal, today_iso):
    """Ask how the step felt, once per completed day, and adapt the pace."""
    feedback = goal.setdefault("feedback", {})
    if today_iso in feedback:
        answers = {
            "easier": "Noted — steps will stay gentler. 💚",
            "ok": "Great — keeping this pace. 👌",
            "harder": "Noted — stepping it up. 💪",
        }
        st.caption(answers.get(feedback[today_iso], ""))
        return

    st.caption("How did that feel? Your answer changes the size of future steps.")
    f1, f2, f3 = st.columns(3)
    choices = [
        (f1, "Too easy 💪", "harder", 1),
        (f2, "Just right 👌", "ok", 0),
        (f3, "Too hard 😮‍💨", "easier", -1),
    ]
    for col, label, value, delta in choices:
        if col.button(label, key=f"fb_{value}_{goal['id']}", use_container_width=True):
            feedback[today_iso] = value
            goal["level_offset"] = max(
                -MAX_OFFSET, min(MAX_OFFSET, level_offset(goal) + delta)
            )
            save_data(st.session_state.data)
            st.rerun()


def render_note(goal, today_iso):
    """Optional one-line journal entry — the record of how far you've come.

    Deliberately a plain input plus button rather than st.form: a form holds an
    open context that survives an interrupted script run and then breaks every
    later st.button on the page.
    """
    notes = goal.setdefault("notes", {})
    key = f"note_{goal['id']}_{today_iso}"
    if key not in st.session_state:
        st.session_state[key] = notes.get(today_iso, "")
    st.text_input(
        "📝 One line about how it went (optional)",
        key=key,
        placeholder="Nervous but I did it. Easier than last week.",
    )
    if st.button("Save note", key=f"save_{key}"):
        text = st.session_state.get(key, "").strip()
        if text:
            notes[today_iso] = text
        else:
            notes.pop(today_iso, None)
        save_data(st.session_state.data)
        st.rerun()


def render_progress_extras(goal, days_done):
    earned, upcoming = milestones_for(days_done)

    with st.expander(f"🏅 Milestones ({len(earned)}/{len(MILESTONES)})", expanded=bool(earned)):
        if earned:
            st.markdown(" ".join(f"{e[1]} **{e[2]}**" for e in earned))
        else:
            st.caption("Complete your first task to unlock your first badge.")
        if upcoming:
            need = upcoming[0] - days_done
            st.caption(
                f"Next: {upcoming[1]} {upcoming[2]} — {need} more task{'s' if need != 1 else ''} to go."
            )
        else:
            st.caption("Every badge earned. Genuinely impressive. 🏆")

    with st.expander("📅 Your last 12 weeks"):
        st.caption("Mon → Sun, one row per week. 🟩 done · ⬜ missed")
        st.markdown(
            "\n".join(f"<div style='letter-spacing:2px'>{r}</div>" for r in heatmap_rows(goal)),
            unsafe_allow_html=True,
        )

    notes = goal.get("notes", {})
    if notes:
        with st.expander(f"📖 Your journey ({len(notes)} notes)"):
            st.caption("Read your first entries — that's the change you can't feel day to day.")
            for day in sorted(notes, reverse=True):
                st.markdown(f"**{day}** — {notes[day]}")


def render_goal(goal):
    lib = GOAL_LIBRARY[goal["category"]]
    total, day_index = goal_days(goal)
    today_iso = date.today().isoformat()
    done_today = today_iso in goal.get("completed_dates", [])
    finished = day_index >= total
    streak, shields = compute_streak(goal)
    days_done = len(goal.get("completed_dates", []))

    st.subheader(f"{lib['emoji']} {goal['name']}")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Day", f"{min(day_index + 1, total)} / {total}")
    c2.metric("Streak", f"🔥 {streak}")
    c3.metric("Shields", f"🛡️ {shields}")
    c4.metric("Tasks done", days_done)
    st.caption("🛡️ Every 7 completed tasks earns a shield that auto-covers one missed day.")

    pct = min(max(day_index, 0) / total, 1.0)
    st.progress(pct, text=f"{int(pct * 100)}% through your timeline")

    if lib.get("support_note"):
        st.warning(lib["support_note"], icon="💛")

    if finished:
        st.success(
            f"🎉 **You made it to the end of your {total}-day journey!** "
            f"You completed {days_done} daily tasks. Look how far you've come."
        )
        render_progress_extras(goal, days_done)
        col_a, col_b = st.columns(2)
        if col_a.button("Keep going — extend 30 days", key=f"ext_{goal['id']}", use_container_width=True):
            goal["end_date"] = (date.fromisoformat(goal["end_date"]) + timedelta(days=30)).isoformat()
            save_data(st.session_state.data)
            st.rerun()
        if col_b.button("Finish & remove this goal", key=f"fin_{goal['id']}", use_container_width=True):
            st.session_state.data["goals"] = [
                g for g in st.session_state.data["goals"] if g["id"] != goal["id"]
            ]
            save_data(st.session_state.data)
            st.rerun()
        return

    # --- today's task ---
    easier = st.session_state.get(f"easier_{goal['id']}", False)
    lvl_idx, lvl_title, task = task_for_day(goal, level_offset=-1 if easier else 0)
    num_levels = len(levels_for(goal))
    pace, _ = pace_label(total, num_levels)

    st.markdown(f"**Level {lvl_idx + 1} of {num_levels}: {lvl_title}** · {pace}")
    if easier:
        st.caption("Showing a gentler step from the previous level — still counts. 💚")

    if done_today:
        st.success(f"✅ **Done for today!** You showed up. That's the whole game.\n\n~~{task}~~")
        hit = next((m for m in MILESTONES if m[0] == days_done), None)
        if hit:
            st.success(f"{hit[1]} **Milestone unlocked — {hit[2]}!** {days_done} tasks done.")
        render_feedback(goal, today_iso)
        render_note(goal, today_iso)
    else:
        st.info(f"### 📌 Today's tiny step\n\n{task}")
        b1, b2 = st.columns([2, 1])
        if b1.button("I did it ✅", key=f"done_{goal['id']}", type="primary", use_container_width=True):
            goal.setdefault("completed_dates", []).append(today_iso)
            save_data(st.session_state.data)
            st.session_state.pop(f"easier_{goal['id']}", None)
            st.balloons()
            st.rerun()
        if lvl_idx > 0 and not easier:
            if b2.button("Too big today", key=f"ez_{goal['id']}", use_container_width=True,
                         help="Get a smaller step from the previous level instead"):
                st.session_state[f"easier_{goal['id']}"] = True
                st.rerun()

    render_progress_extras(goal, days_done)

    # --- ladder overview ---
    with st.expander("🪜 See your full ladder"):
        off = level_offset(goal)
        if off:
            direction = "harder" if off > 0 else "gentler"
            st.caption(
                f"Your feedback has shifted you {abs(off)} level(s) {direction} than the timeline's default pace."
            )
        for i, level in enumerate(levels_for(goal)):
            if i < lvl_idx:
                st.markdown(f"~~**Level {i + 1}: {level['title']}**~~ ✅")
            elif i == lvl_idx:
                st.markdown(f"➡️ **Level {i + 1}: {level['title']}** ← you are here")
            else:
                st.markdown(f"🔒 Level {i + 1}: {level['title']}")

    with st.expander("⚙️ Goal settings"):
        st.caption(
            f"Started {goal['start_date']} · target {goal['end_date']} · "
            f"{max(total - day_index, 0)} days left"
        )
        if level_offset(goal) and st.button(
            "Reset difficulty to the timeline's pace", key=f"rst_{goal['id']}"
        ):
            goal["level_offset"] = 0
            save_data(st.session_state.data)
            st.rerun()
        if st.button("Delete this goal", key=f"del_{goal['id']}"):
            st.session_state.data["goals"] = [
                g for g in st.session_state.data["goals"] if g["id"] != goal["id"]
            ]
            save_data(st.session_state.data)
            st.rerun()


# --------------------------------------------------------------------- app ---

st.title("🌱 Tiny Steps")
st.caption("Get better at anything — one baby step a day.")

goals = st.session_state.data["goals"]

if not goals:
    render_add_goal(first_goal=True)
else:
    done_today = sum(1 for g in goals if date.today().isoformat() in g.get("completed_dates", []))
    if done_today == len(goals):
        st.success(f"All {len(goals)} task(s) done today. Rest easy — you earned it. 😌")
    else:
        st.caption(f"✅ {done_today} of {len(goals)} tasks done today")

    if len(goals) == 1:
        render_goal(goals[0])
    else:
        tabs = st.tabs([f"{GOAL_LIBRARY[g['category']]['emoji']} {g['name']}" for g in goals])
        for tab, goal in zip(tabs, goals):
            with tab:
                render_goal(goal)

    st.divider()
    if st.session_state.get("adding_goal"):
        st.markdown("### ➕ Add another goal")
        render_add_goal()
        if st.button("Cancel"):
            st.session_state.pop("adding_goal", None)
            st.rerun()
    else:
        if st.button("➕ Work on something else too"):
            st.session_state["adding_goal"] = True
            st.rerun()
