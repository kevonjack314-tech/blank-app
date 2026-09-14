import html
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
    """Week rows (Monday-aligned) of 'done' | 'missed' | 'outside' cells.

    Returns the same structure as heatmapRows() in mobile/src/logic.js so both
    apps draw an identical grid; each surface picks its own colours.
    """
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
                cells.append("outside")
            elif day.isoformat() in done:
                cells.append("done")
            else:
                cells.append("missed")
            day += timedelta(days=1)
        rows.append(cells)
    # Drop whole weeks that fall entirely before the journey began — a new goal
    # shouldn't open on six rows of blank squares.
    while len(rows) > 1 and all(c == "outside" for c in rows[0]):
        rows.pop(0)
    return rows


# ------------------------------------------------------------------ chrome ---

def esc(text):
    return html.escape(str(text))


MOBILE_CSS = """
<style>
/* Phone-first layout: narrow gutters, room for thumbs, no sideways scroll. */
.block-container {max-width: 46rem; padding-top: 2.4rem; padding-bottom: 4rem;}
@media (max-width: 640px) {
  .block-container {padding-left: .85rem; padding-right: .85rem; padding-top: 1.5rem;}
  h1 {font-size: 1.65rem !important;}
}
section.main {overflow-x: hidden;}
.stButton > button {min-height: 46px; border-radius: 12px; font-weight: 600;}

/* Today card */
.ts-card {background: rgba(46,125,79,.06); border: 1px solid rgba(46,125,79,.18);
          border-radius: 16px; padding: 14px 16px 16px; margin: 4px 0 12px;}
.ts-card.ts-done {background: rgba(0,0,0,.03); border-color: rgba(0,0,0,.08);}
.ts-title {font-size: 1.05rem; font-weight: 800; margin: 0 0 8px;}
.ts-chips {display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 12px;}
.ts-chip {background: rgba(46,125,79,.14); color: #2e7d4f; border-radius: 999px;
          padding: 3px 10px; font-size: .78rem; font-weight: 700; white-space: nowrap;}
.ts-label {font-size: .7rem; letter-spacing: .09em; text-transform: uppercase;
           opacity: .6; font-weight: 800; margin: 0 0 4px;}
.ts-task {font-size: 1.12rem; line-height: 1.5; font-weight: 600; margin: 0;}
.ts-done .ts-task {text-decoration: line-through; opacity: .6; font-weight: 500;}

/* Heatmap: seven square columns that always fit the screen */
.ts-hm {display: grid; grid-template-columns: repeat(7, 1fr); gap: 4px; max-width: 320px;}
.ts-hm i {aspect-ratio: 1; border-radius: 3px; display: block;}
.ts-hm .d {background: #2e7d4f;}
.ts-hm .m {background: rgba(0,0,0,.10);}
.ts-hm .o {background: rgba(0,0,0,.02);}
</style>
"""


# ---------------------------------------------------------------- add goal ---

def render_add_goal(first_goal=False):
    if first_goal:
        st.markdown(
            "Pick something you want to get better at. Every day you'll get "
            "**one small task** — starting so easy it feels silly."
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


# ----------------------------------------------------------- today's card ---

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
        "One line about how it went",
        key=key,
        placeholder="Nervous but I did it. Easier than last week.",
    )
    if st.button("Save note", key=f"save_{key}", use_container_width=True):
        text = st.session_state.get(key, "").strip()
        if text:
            notes[today_iso] = text
        else:
            notes.pop(today_iso, None)
        save_data(st.session_state.data)
        st.rerun()


def card_html(goal, chips, label, task, done):
    lib = GOAL_LIBRARY[goal["category"]]
    chip_html = "".join(f'<span class="ts-chip">{esc(c)}</span>' for c in chips)
    return (
        f'<div class="ts-card{" ts-done" if done else ""}">'
        f'<p class="ts-title">{lib["emoji"]} {esc(goal["name"])}</p>'
        f'<div class="ts-chips">{chip_html}</div>'
        f'<p class="ts-label">{esc(label)}</p>'
        f'<p class="ts-task">{esc(task)}</p>'
        f"</div>"
    )


def render_finished(goal, total, days_done):
    st.markdown(
        card_html(
            goal,
            [f"{total} days", f"{days_done} tasks done"],
            "journey complete",
            "You made it to the end. Look how far you've come. 🎉",
            done=True,
        ),
        unsafe_allow_html=True,
    )
    c1, c2 = st.columns(2)
    if c1.button("Keep going — +30 days", key=f"ext_{goal['id']}",
                 type="primary", use_container_width=True):
        goal["end_date"] = (date.fromisoformat(goal["end_date"]) + timedelta(days=30)).isoformat()
        save_data(st.session_state.data)
        st.rerun()
    if c2.button("Finish & remove", key=f"fin_{goal['id']}", use_container_width=True):
        st.session_state.data["goals"] = [
            g for g in st.session_state.data["goals"] if g["id"] != goal["id"]
        ]
        save_data(st.session_state.data)
        st.rerun()


def render_goal_card(goal):
    """The whole daily loop — see today's step and check it off — in one card."""
    lib = GOAL_LIBRARY[goal["category"]]
    total, day_index = goal_days(goal)
    today_iso = date.today().isoformat()
    completed = goal.get("completed_dates", [])
    done_today = today_iso in completed
    days_done = len(completed)

    if day_index >= total:
        render_finished(goal, total, days_done)
        return

    streak, shields = compute_streak(goal)
    easier = st.session_state.get(f"easier_{goal['id']}", False)
    lvl_idx, lvl_title, task = task_for_day(goal, level_offset=-1 if easier else 0)
    levels = levels_for(goal)

    chips = [f"Day {min(day_index + 1, total)}/{total}"]
    if streak:
        chips.append(f"🔥 {streak}")
    if shields:
        chips.append(f"🛡️ {shields}")
    chips.append(f"Level {lvl_idx + 1}/{len(levels)}: {lvl_title}")

    st.markdown(
        card_html(
            goal,
            chips,
            "✅ done today" if done_today else "📌 today's tiny step",
            task,
            done_today,
        ),
        unsafe_allow_html=True,
    )

    if easier and not done_today:
        st.caption("A gentler step from the previous level — it still counts. 💚")

    if done_today:
        hit = next((m for m in MILESTONES if m[0] == days_done), None)
        if hit:
            st.success(f"{hit[1]} **Milestone unlocked — {hit[2]}!** {days_done} tasks done.")
        render_feedback(goal, today_iso)
        with st.expander("📝 Add a note about today"):
            render_note(goal, today_iso)
        u1, _ = st.columns([1, 2])
        if u1.button("↩️ Undo", key=f"undo_{goal['id']}", use_container_width=True,
                     help="Checked in by mistake? This removes today's check-in."):
            goal["completed_dates"] = [d for d in completed if d != today_iso]
            goal.get("feedback", {}).pop(today_iso, None)
            save_data(st.session_state.data)
            st.rerun()
    else:
        if st.button("I did it ✅", key=f"done_{goal['id']}",
                     type="primary", use_container_width=True):
            goal.setdefault("completed_dates", []).append(today_iso)
            save_data(st.session_state.data)
            st.session_state.pop(f"easier_{goal['id']}", None)
            st.balloons()
            st.rerun()
        if lvl_idx > 0 and not easier:
            if st.button("Too big today — give me a smaller step",
                         key=f"ez_{goal['id']}", use_container_width=True):
                st.session_state[f"easier_{goal['id']}"] = True
                st.rerun()

    if lib.get("support_note"):
        st.warning(lib["support_note"], icon="💛")


# ------------------------------------------------------- progress & setup ---

HM_CLASS = {"done": "d", "missed": "m", "outside": "o"}


def render_heatmap(goal):
    cells = "".join(
        f'<i class="{HM_CLASS[cell]}"></i>'
        for row in heatmap_rows(goal)
        for cell in row
    )
    st.markdown(f'<div class="ts-hm">{cells}</div>', unsafe_allow_html=True)
    st.caption("Mon → Sun, one row per week. Green = you showed up.")


def render_details(goal):
    """Everything that isn't today: stats, badges, history, ladder, settings."""
    total, day_index = goal_days(goal)
    completed = goal.get("completed_dates", [])
    days_done = len(completed)
    streak, shields = compute_streak(goal)
    earned, upcoming = milestones_for(days_done)
    levels = levels_for(goal)
    lvl_now = current_level_index(goal)

    with st.expander("📊 Progress"):
        # Chips rather than st.metric: metrics stack to one per row on a phone,
        # turning three numbers into a long scroll.
        stats = [f"🔥 {streak} streak", f"🛡️ {shields} shields", f"✅ {days_done} tasks done"]
        st.markdown(
            '<div class="ts-chips">'
            + "".join(f'<span class="ts-chip">{esc(s)}</span>' for s in stats)
            + "</div>",
            unsafe_allow_html=True,
        )
        st.caption("🛡️ Every 7 completed tasks earns a shield that auto-covers one missed day.")

        pct = min(max(day_index, 0) / total, 1.0)
        st.progress(pct, text=f"{int(pct * 100)}% through your {total}-day timeline")

        st.markdown(f"**🏅 Milestones ({len(earned)}/{len(MILESTONES)})**")
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

        st.markdown("**📅 Your last 12 weeks**")
        render_heatmap(goal)

    notes = goal.get("notes", {})
    if notes:
        with st.expander(f"📖 Your journey ({len(notes)} notes)"):
            st.caption("Read your first entries — that's the change you can't feel day to day.")
            for day in sorted(notes, reverse=True):
                st.markdown(f"**{day}** — {notes[day]}")

    with st.expander("🪜 Your ladder"):
        off = level_offset(goal)
        if off:
            st.caption(
                f"Your feedback has shifted you {abs(off)} level(s) "
                f"{'harder' if off > 0 else 'gentler'} than the timeline's default pace."
            )
        for i, level in enumerate(levels):
            if i < lvl_now:
                st.markdown(f"~~**Level {i + 1}: {level['title']}**~~ ✅")
            elif i == lvl_now:
                st.markdown(f"➡️ **Level {i + 1}: {level['title']}** ← you are here")
            else:
                st.markdown(f"🔒 Level {i + 1}: {level['title']}")

    with st.expander("⚙️ Settings"):
        st.caption(
            f"Started {goal['start_date']} · target {goal['end_date']} · "
            f"{max(total - day_index, 0)} days left"
        )
        if level_offset(goal) and st.button(
            "Reset difficulty to the timeline's pace", key=f"rst_{goal['id']}",
            use_container_width=True,
        ):
            goal["level_offset"] = 0
            save_data(st.session_state.data)
            st.rerun()

        confirm_key = f"confirm_del_{goal['id']}"
        if st.session_state.get(confirm_key):
            st.warning(f"Delete **{goal['name']}** and its {days_done} completed tasks? "
                       "This can't be undone.")
            d1, d2 = st.columns(2)
            if d1.button("Yes, delete", key=f"del_yes_{goal['id']}", use_container_width=True):
                st.session_state.data["goals"] = [
                    g for g in st.session_state.data["goals"] if g["id"] != goal["id"]
                ]
                save_data(st.session_state.data)
                st.session_state.pop(confirm_key, None)
                st.rerun()
            if d2.button("Cancel", key=f"del_no_{goal['id']}", use_container_width=True):
                st.session_state.pop(confirm_key, None)
                st.rerun()
        elif st.button("Delete this goal", key=f"del_{goal['id']}", use_container_width=True):
            st.session_state[confirm_key] = True
            st.rerun()


# --------------------------------------------------------------------- app ---

st.markdown(MOBILE_CSS, unsafe_allow_html=True)
st.title("🌱 Tiny Steps")

goals = st.session_state.data["goals"]

if not goals:
    st.caption("Get better at anything — one baby step a day.")
    render_add_goal(first_goal=True)
else:
    today_iso = date.today().isoformat()
    done_today = sum(1 for g in goals if today_iso in g.get("completed_dates", []))
    active = [g for g in goals if goal_days(g)[1] < goal_days(g)[0]]
    if active and done_today >= len(active):
        st.success("Everything done today. Rest easy — you earned it. 😌")
    else:
        st.caption(f"✅ {done_today} of {len(active)} done today")

    for i, goal in enumerate(goals):
        render_goal_card(goal)
        render_details(goal)
        if i < len(goals) - 1:
            st.divider()

    st.divider()
    with st.expander("➕ Work on something else too"):
        render_add_goal()
