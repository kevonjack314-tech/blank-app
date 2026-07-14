"""Persistence for Tiny Steps.

If Supabase credentials are present in Streamlit secrets (SUPABASE_URL and
SUPABASE_KEY), progress is stored in a `tiny_steps` table there, so it
survives Streamlit Cloud redeploys and restarts. Without credentials the app
falls back to a local `user_data.json` next to the app. The local file is
always written too, as a backup and as a cache for the current container.

Expected table (see README for setup):

    create table tiny_steps (
      id text primary key,
      data jsonb not null,
      updated_at timestamptz default now()
    );
"""

import json
from pathlib import Path

import requests
import streamlit as st

DATA_FILE = Path(__file__).parent / "user_data.json"
TABLE = "tiny_steps"
ROW_ID = "default"


def _empty():
    # Fresh object every call — a shared constant's inner list would be
    # mutated by goal appends and leak across sessions.
    return {"goals": []}


def _supabase_conf():
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
    except (KeyError, FileNotFoundError):
        return None
    if not url or not key:
        return None
    return url.rstrip("/"), key


def _headers(key):
    return {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }


def _load_local():
    if DATA_FILE.exists():
        try:
            return json.loads(DATA_FILE.read_text())
        except (json.JSONDecodeError, OSError):
            return _empty()
    return _empty()


def _save_local(data):
    try:
        DATA_FILE.write_text(json.dumps(data, indent=2))
    except OSError:
        pass


def load_data():
    conf = _supabase_conf()
    if conf:
        url, key = conf
        try:
            r = requests.get(
                f"{url}/rest/v1/{TABLE}",
                params={"id": f"eq.{ROW_ID}", "select": "data"},
                headers=_headers(key),
                timeout=10,
            )
            r.raise_for_status()
            rows = r.json()
            data = rows[0]["data"] if rows else _empty()
            _save_local(data)
            return data
        except (requests.RequestException, ValueError, KeyError, IndexError) as e:
            st.warning(
                f"Couldn't reach cloud storage ({e}). Using local data for now — "
                "changes will sync next time saving succeeds."
            )
    return _load_local()


def save_data(data):
    _save_local(data)
    conf = _supabase_conf()
    if not conf:
        return
    url, key = conf
    try:
        r = requests.post(
            f"{url}/rest/v1/{TABLE}",
            headers={**_headers(key), "Prefer": "resolution=merge-duplicates"},
            json=[{"id": ROW_ID, "data": data}],
            timeout=10,
        )
        r.raise_for_status()
    except requests.RequestException as e:
        st.warning(f"Saved locally, but cloud sync failed ({e}). Will retry on your next check-in.")
