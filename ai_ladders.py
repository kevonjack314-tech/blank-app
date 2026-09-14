"""AI-generated task ladders for custom goals.

When an ANTHROPIC_API_KEY is present in Streamlit secrets, custom goals get a
personalized 8-level ladder built by Claude instead of the generic
habit-building one. The generated ladder is stored on the goal itself
(goal["custom_levels"]), so the mobile app and future sessions use it without
calling the API again. Without a key (or on any failure) the app quietly
falls back to the generic ladder.
"""

import json

import anthropic
import streamlit as st

MODEL = "claude-opus-4-8"

LADDER_SCHEMA = {
    "type": "object",
    "properties": {
        "levels": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "tasks": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                },
                "required": ["title", "tasks"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["levels"],
    "additionalProperties": False,
}

PROMPT = """You are designing a daily-practice ladder for a self-improvement app \
called Tiny Steps. The user picks a goal and a timeline; every day the app gives \
them exactly one small task. Levels progress from "embarrassingly easy" to \
"the real deal", and the app paces the climb to the timeline.

The user's goal: {goal}
Their timeline: {days} days.

Create a ladder of exactly 8 levels for this goal. Requirements:
- Level 1 tasks must be tiny baby steps doable in under 5 minutes by a complete \
beginner with zero confidence — the point is just to start.
- Each level should be a clear notch harder than the previous; level 8 tasks are \
genuinely challenging but achievable for someone who climbed the ladder.
- Each level has a short title (2-4 words) and exactly 3 task variants, so daily \
tasks don't repeat word for word.
- Each task is one concrete action for a single day, written directly to the \
user ("Write down...", "Do 5 minutes of..."), specific and measurable, never \
vague advice like "practice more".
- Tasks must be safe and realistic; require no special equipment unless the \
goal implies it.
- If the goal touches addiction, mental health, or anything medically risky, \
keep tasks gentle and supportive and make one early task about finding real \
support (a professional, a helpline, or a support group)."""


def _client():
    try:
        key = st.secrets["ANTHROPIC_API_KEY"]
    except (KeyError, FileNotFoundError):
        return None
    if not key:
        return None
    try:
        base_url = st.secrets["ANTHROPIC_BASE_URL"]
    except (KeyError, FileNotFoundError):
        base_url = None
    # Generation happens behind a UI spinner, so cap the wait well below the
    # SDK's 10-minute default; on failure the app falls back to the generic ladder.
    kwargs = {"api_key": key, "timeout": 90.0, "max_retries": 1}
    if base_url:
        kwargs["base_url"] = base_url
    return anthropic.Anthropic(**kwargs)


def ai_available():
    return _client() is not None


def _valid(levels):
    if not isinstance(levels, list) or not 5 <= len(levels) <= 10:
        return False
    for level in levels:
        if not level.get("title") or not isinstance(level.get("tasks"), list):
            return False
        if len(level["tasks"]) < 2 or not all(isinstance(t, str) and t for t in level["tasks"]):
            return False
    return True


def generate_ladder(goal_name, total_days):
    """Return a list of levels for the goal, or None to use the generic ladder."""
    client = _client()
    if client is None:
        return None
    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=16000,
            thinking={"type": "adaptive"},
            output_config={"format": {"type": "json_schema", "schema": LADDER_SCHEMA}},
            messages=[
                {"role": "user", "content": PROMPT.format(goal=goal_name, days=total_days)}
            ],
        )
        if response.stop_reason == "refusal":
            return None
        text = next(b.text for b in response.content if b.type == "text")
        levels = json.loads(text)["levels"]
        return levels if _valid(levels) else None
    except (anthropic.APIError, StopIteration, ValueError, KeyError, TypeError):
        return None
