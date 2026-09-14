"""End-to-end tests for the Tiny Steps web app, driven through Streamlit's AppTest."""

import sys
from datetime import date

from conftest import (  # noqa: E402 - path is set up in conftest
    a_goal,
    card_html,
    click,
    days_ago,
    in_days,
    input_by_label,
    open_app,
    read_goals,
    run_suite,
    text_of,
    write_goals,
)

TODAY = date.today().isoformat()


# ------------------------------------------------------------- onboarding ---

def test_first_run_offers_every_goal_area():
    at = open_app()
    labels = at.selectbox[0].options
    for name in [
        "Social Anxiety", "Communicate Better", "Sleep Better", "Beat Procrastination",
        "Manage Anger", "Save Money", "Meditate Regularly", "Quit Vaping",
    ]:
        assert any(name in o for o in labels), f"{name} missing from the picker"
    assert any("custom" in o.lower() for o in labels)


def test_creating_a_goal_starts_the_journey():
    at = open_app()
    labels = at.selectbox[0].options
    at.selectbox[0].select([o for o in labels if "Sleep Better" in o][0])
    at.selectbox[1].select("2 months")
    at.run()
    at = click(at, "Start this journey")

    goal = read_goals()[0]
    assert goal["category"] == "sleep"
    assert (date.fromisoformat(goal["end_date"]) - date.fromisoformat(goal["start_date"])).days == 60

    at = open_app()
    assert "tiny step" in text_of(at).lower()


def test_custom_goal_requires_a_name():
    at = open_app()
    labels = at.selectbox[0].options
    at.selectbox[0].select([o for o in labels if "custom" in o.lower()][0])
    at.run()
    at = click(at, "Start this journey")
    assert "name" in text_of(at).lower()
    assert read_goals() == [], "a nameless custom goal must not be created"


# ------------------------------------------------------------ daily loop ---

def test_today_card_shows_the_task_and_checks_it_off():
    at = open_app([a_goal()])
    body = text_of(at)
    assert "tiny step" in body.lower()
    assert '<div class="ts-card' in body, "today card markup missing"

    at = click(at, "I did it")
    assert read_goals()[0]["completed_dates"] == [TODAY]

    at = open_app()
    assert "done today" in text_of(at).lower()


def test_undo_removes_todays_check_in():
    at = open_app([a_goal(completed_dates=[TODAY], feedback={TODAY: "ok"})])
    at = click(at, "Undo")
    goal = read_goals()[0]
    assert goal["completed_dates"] == []
    assert TODAY not in goal.get("feedback", {})
    assert "tiny step" in text_of(open_app()).lower()


def test_too_big_today_offers_a_gentler_step():
    at = open_app([a_goal()])
    at = click(at, "Too big today")
    assert "gentler step" in text_of(at).lower()


# --------------------------------------------------- adaptive difficulty ---

def _level_line(at):
    return next(line for line in text_of(at).splitlines() if "Level " in line)


def test_feedback_raises_and_lowers_difficulty():
    at = open_app([a_goal(completed_dates=[TODAY])])
    before = _level_line(at)
    at = click(at, "Too easy")
    assert read_goals()[0]["level_offset"] == 1
    assert _level_line(open_app()) != before

    at = open_app([a_goal(completed_dates=[TODAY])])
    at = click(at, "Too hard")
    assert read_goals()[0]["level_offset"] == -1


def test_difficulty_is_clamped_and_resettable():
    at = open_app([a_goal(completed_dates=[TODAY], level_offset=3)])
    at = click(at, "Too easy")
    assert read_goals()[0]["level_offset"] == 3, "offset should clamp at +3"

    at = open_app()
    at = click(at, "Reset difficulty")
    assert read_goals()[0]["level_offset"] == 0


def test_a_garbage_offset_never_breaks_the_app():
    at = open_app([a_goal(level_offset="not a number")])
    assert "tiny step" in text_of(at).lower()


# ---------------------------------------------------- notes & milestones ---

def test_note_saves_appears_in_the_journey_and_clears():
    at = open_app([a_goal(completed_dates=[TODAY])])
    input_by_label(at, "how it went").set_value("Nervous but I said hi.").run()
    at = click(at, "Save note")
    assert read_goals()[0]["notes"][TODAY] == "Nervous but I said hi."

    at = open_app()
    assert "Nervous but I said hi." in text_of(at)

    input_by_label(at, "how it went").set_value("").run()
    at = click(at, "Save note")
    assert TODAY not in read_goals()[0].get("notes", {})


def test_milestone_unlocks_at_seven_tasks():
    at = open_app([a_goal(completed_dates=[days_ago(i) for i in range(7)])])
    body = text_of(at)
    assert "Milestone unlocked" in body and "One week" in body
    assert "⭐ **One week**" in body
    assert "Two weeks" in body, "next milestone hint missing"


def test_heatmap_renders_whole_weeks_without_leading_blanks():
    at = open_app([a_goal(completed_dates=[TODAY])])
    grid = next(m.value for m in at.markdown if 'class="ts-hm"' in str(m.value))
    cells = grid.count("<i ")
    assert cells % 7 == 0 and 0 < cells <= 12 * 7, cells
    assert grid.count('<i class="d">') == 1, "today should be the only completed cell"
    assert '<i class="m">' in grid


def test_a_brand_new_goal_does_not_show_blank_weeks():
    at = open_app([a_goal(start_date=TODAY, end_date=in_days(60), completed_dates=[TODAY])])
    grid = next(m.value for m in at.markdown if 'class="ts-hm"' in str(m.value))
    assert grid.count("<i ") == 7, "a day-one goal should show a single week"


# --------------------------------------------------------- goal lifecycle ---

def test_finished_goal_can_be_extended():
    at = open_app([a_goal(start_date=days_ago(61), end_date=days_ago(1))])
    assert "journey complete" in text_of(at).lower()
    at = click(at, "Keep going")
    assert date.fromisoformat(read_goals()[0]["end_date"]) > date.today()


def test_delete_needs_confirmation():
    at = open_app([a_goal()])
    at = click(at, "Delete this goal")
    assert read_goals(), "goal must survive the first click"
    assert "can't be undone" in text_of(at).lower()

    at = click(at, "Cancel")
    assert read_goals(), "cancel must keep the goal"

    at = click(at, "Delete this goal")
    at = click(at, "Yes, delete")
    assert read_goals() == []


def test_multiple_goals_each_get_their_own_card():
    second = a_goal(id="g2", category="reading", name="Read More")
    at = open_app([a_goal(), second])
    body = text_of(at)
    assert "Overcome Social Anxiety" in body and "Read More" in body
    assert body.count('<div class="ts-card') >= 2
    assert "0 of 2 done today" in body


# -------------------------------------------------------------- security ---

def test_custom_goal_names_are_escaped_not_injected():
    nasty = '<img src=x onerror=alert(1)>"evil"'
    at = open_app([a_goal(category="custom", name=nasty)])
    card = card_html(at)
    assert "<img" not in card, "raw HTML from a goal name reached the page"
    assert "&lt;img" in card


if __name__ == "__main__":
    print("Tiny Steps — web app tests")
    sys.exit(run_suite(dict(globals())))
