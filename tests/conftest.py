"""Shared helpers for the Streamlit app tests.

Run everything with `python3 tests/test_app.py` (no pytest needed) or with
`pytest tests/`.
"""

import json
import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

APP = str(ROOT / "streamlit_app.py")
DATA = ROOT / "user_data.json"


def write_goals(goals):
    DATA.write_text(json.dumps({"goals": goals}))


def read_goals():
    """Goals as persisted on disk (empty list if nothing has been saved yet)."""
    if not DATA.exists():
        return []
    return json.loads(DATA.read_text())["goals"]


def card_html(at):
    """The rendered today-card markup (skipping the stylesheet block)."""
    cards = [str(m.value) for m in at.markdown if '<div class="ts-card' in str(m.value)]
    assert cards, "no today card rendered"
    return cards[0]


def clear():
    DATA.unlink(missing_ok=True)


def days_ago(n):
    return (date.today() - timedelta(days=n)).isoformat()


def in_days(n):
    return (date.today() + timedelta(days=n)).isoformat()


def a_goal(**overrides):
    """A goal 30 days into a 60-day journey."""
    goal = {
        "id": "g1",
        "category": "social_anxiety",
        "name": "Overcome Social Anxiety",
        "start_date": days_ago(30),
        "end_date": in_days(30),
        "completed_dates": [],
    }
    goal.update(overrides)
    return goal


def open_app(goals=None, secrets=None, timeout=60):
    """Start the app, optionally seeded with goals, and assert it rendered."""
    from streamlit.testing.v1 import AppTest

    if goals is not None:
        write_goals(goals)
    at = AppTest.from_file(APP, default_timeout=timeout)
    if secrets:
        at.secrets.update(secrets)
    at.run()
    assert not at.exception, at.exception
    return at


def click(at, needle):
    """Click the first button whose label contains `needle`."""
    matches = [b for b in at.button if needle.lower() in b.label.lower()]
    assert matches, f"no button matching {needle!r}; have {[b.label for b in at.button]}"
    at = matches[0].click().run()
    assert not at.exception, at.exception
    return at


def text_of(at):
    """All rendered markdown, captions, info, success and warning text."""
    parts = []
    for group in (at.markdown, at.caption, at.info, at.success, at.warning, at.error):
        parts += [str(e.value) for e in group]
    return "\n".join(parts)


def input_by_label(at, needle):
    matches = [t for t in at.text_input if needle.lower() in (t.label or "").lower()]
    assert matches, f"no input matching {needle!r}; have {[t.label for t in at.text_input]}"
    return matches[0]


def run_suite(module_globals):
    """Run every test_* function in a module and report pass/fail."""
    tests = sorted(
        (name, fn) for name, fn in module_globals.items()
        if name.startswith("test_") and callable(fn)
    )
    failures = 0
    for name, fn in tests:
        clear()
        try:
            fn()
            print(f"  ok   {name}")
        except Exception as exc:  # noqa: BLE001 - report and continue
            failures += 1
            print(f"  FAIL {name}: {type(exc).__name__}: {exc}")
    clear()
    print(f"\n{len(tests) - failures}/{len(tests)} passed")
    return 1 if failures else 0
