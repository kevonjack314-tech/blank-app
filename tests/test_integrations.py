"""Tests for the two optional integrations: Supabase sync and AI-built ladders.

Both run against local fake servers, so no credentials or network are needed.
"""

import json
import sys
import threading
from datetime import date
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from conftest import (  # noqa: E402 - path is set up in conftest
    DATA,
    a_goal,
    click,
    clear,
    input_by_label,
    open_app,
    read_goals,
    run_suite,
    text_of,
)

TODAY = date.today().isoformat()


def _serve(handler_cls, port):
    server = ThreadingHTTPServer(("127.0.0.1", port), handler_cls)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


# ------------------------------------------------------------- supabase ---

class FakeSupabase(BaseHTTPRequestHandler):
    store = {}
    requests = []

    def log_message(self, *args):
        pass

    def _send(self, code, body=b""):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        FakeSupabase.requests.append(("GET", dict(self.headers)))
        rows = [{"data": FakeSupabase.store["default"]}] if "default" in FakeSupabase.store else []
        self._send(200, json.dumps(rows).encode())

    def do_POST(self):
        payload = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        FakeSupabase.requests.append(("POST", dict(self.headers)))
        for row in payload:
            FakeSupabase.store[row["id"]] = row["data"]
        self._send(201)


SUPABASE_SECRETS = {"SUPABASE_URL": "http://127.0.0.1:8765", "SUPABASE_KEY": "test-key"}


def test_progress_syncs_to_the_cloud_and_survives_a_wiped_device():
    FakeSupabase.store.clear()
    FakeSupabase.requests.clear()
    FakeSupabase.store["default"] = {"goals": [a_goal()]}
    server = _serve(FakeSupabase, 8765)
    try:
        at = open_app(secrets=SUPABASE_SECRETS)
        at = click(at, "I did it")
        assert FakeSupabase.store["default"]["goals"][0]["completed_dates"] == [TODAY]

        post = [r for r in FakeSupabase.requests if r[0] == "POST"][-1]
        assert post[1].get("apikey") == "test-key"
        assert post[1].get("Prefer") == "resolution=merge-duplicates"

        # A redeploy wipes the local file; the cloud copy must restore it.
        clear()
        at = open_app(secrets=SUPABASE_SECRETS)
        assert "done today" in text_of(at).lower()
    finally:
        server.shutdown()
        server.server_close()


def test_cloud_outage_falls_back_to_local_data_with_a_warning():
    at = open_app([a_goal(completed_dates=[TODAY])], secrets=SUPABASE_SECRETS)
    body = text_of(at)
    assert "cloud storage" in body.lower(), "no outage warning shown"
    assert "done today" in body.lower(), "local fallback did not render"


# ------------------------------------------------------------ ai ladders ---

FAKE_LEVELS = [
    {"title": f"Level {i} title", "tasks": [f"L{i} task A", f"L{i} task B", f"L{i} task C"]}
    for i in range(1, 9)
]


class FakeAnthropic(BaseHTTPRequestHandler):
    requests = []

    def log_message(self, *args):
        pass

    def do_POST(self):
        payload = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        FakeAnthropic.requests.append((self.path, payload))
        body = json.dumps({
            "id": "msg_test",
            "type": "message",
            "role": "assistant",
            "model": payload.get("model", "claude-opus-4-8"),
            "content": [{"type": "text", "text": json.dumps({"levels": FAKE_LEVELS})}],
            "stop_reason": "end_turn",
            "stop_sequence": None,
            "usage": {"input_tokens": 100, "output_tokens": 500},
        }).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


AI_SECRETS = {"ANTHROPIC_API_KEY": "test-key", "ANTHROPIC_BASE_URL": "http://127.0.0.1:8766"}


def _start_custom_goal(at, name):
    labels = at.selectbox[0].options
    at.selectbox[0].select([o for o in labels if "custom" in o.lower()][0])
    at.run()
    input_by_label(at, "Name your goal").set_value(name).run()
    return click(at, "Start this journey")


def test_custom_goal_gets_an_ai_built_ladder():
    FakeAnthropic.requests.clear()
    server = _serve(FakeAnthropic, 8766)
    try:
        at = open_app([], secrets=AI_SECRETS)
        labels = at.selectbox[0].options
        at.selectbox[0].select([o for o in labels if "custom" in o.lower()][0])
        at.run()
        assert "AI will build" in text_of(at)
        at = _start_custom_goal(at, "Learn to juggle")

        goal = read_goals()[0]
        assert goal["name"] == "Learn to juggle"
        assert len(goal["custom_levels"]) == 8

        path, payload = FakeAnthropic.requests[-1]
        assert path.endswith("/v1/messages")
        assert "Learn to juggle" in json.dumps(payload)
        assert payload["output_config"]["format"]["type"] == "json_schema"

        # The generated ladder, not the generic one, drives the daily task.
        at = open_app(secrets=AI_SECRETS)
        assert "L1 task" in text_of(at)
    finally:
        server.shutdown()
        server.server_close()


def test_ai_failure_falls_back_to_the_generic_ladder():
    at = open_app([], secrets=AI_SECRETS)
    at = _start_custom_goal(at, "Learn chess")
    goal = read_goals()[0]
    assert goal["name"] == "Learn chess"
    assert "custom_levels" not in goal, "a failed generation must not be stored"


def test_no_api_key_means_no_ai_prompt_and_no_call():
    FakeAnthropic.requests.clear()
    at = open_app([])
    labels = at.selectbox[0].options
    at.selectbox[0].select([o for o in labels if "custom" in o.lower()][0])
    at.run()
    assert "AI will build" not in text_of(at)
    at = _start_custom_goal(at, "Learn pottery")
    assert "custom_levels" not in read_goals()[0]
    assert not FakeAnthropic.requests


if __name__ == "__main__":
    print("Tiny Steps — integration tests (Supabase + AI ladders)")
    sys.exit(run_suite(dict(globals())))
