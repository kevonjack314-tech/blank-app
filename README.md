# 🌱 Tiny Steps — self-improvement, one baby step a day

Pick anything you want to get better at — social anxiety, communication, self-doubt,
addiction recovery, relationship health, reading, fitness, quitting porn, songwriting,
singing, or a custom goal — and the app gives you **one small task every day**.

**The timeline changes the steps.** Tell it how long you want to give yourself:
a 2-month goal climbs the difficulty ladder fast with bigger daily steps, while a
1-year goal moves slow and gradual with the littlest of baby steps and lots of
practice at each stage.

Features:

- 🪜 Every goal is a ladder of levels, from "embarrassingly easy" to "the real deal"
- ⏱️ Timeline picker (2 weeks → 1 year, or a custom date) that paces the ladder
- 🔥 Streaks, progress bar, and daily check-off with multiple goals at once
- 💚 "Too big today" button that swaps in a gentler step from the previous level
- 🎉 End-of-journey celebration with the option to extend 30 days

### Saving your progress

Out of the box, progress is saved to a local `user_data.json` next to the app.
That works fine on your own machine, but on Streamlit Cloud the file is wiped
whenever the app redeploys or restarts.

To make progress permanent, connect a free [Supabase](https://supabase.com)
database:

1. Create a Supabase account and a new project (the free tier is plenty).
2. In the project's **SQL Editor**, run:

   ```sql
   create table tiny_steps (
     id text primary key,
     data jsonb not null,
     updated_at timestamptz default now()
   );
   alter table tiny_steps disable row level security;
   ```

3. In Supabase, go to **Settings → API** and copy the **Project URL** and the
   **anon public** key.
4. In your Streamlit Cloud app, go to **Settings → Secrets** and add:

   ```toml
   SUPABASE_URL = "https://your-project-id.supabase.co"
   SUPABASE_KEY = "your-anon-key"
   ```

   (Running locally, put the same lines in `.streamlit/secrets.toml`.)

That's it — the app detects the credentials and syncs every change to
Supabase, falling back to the local file if the connection ever hiccups.
The keys stay server-side in Streamlit secrets; visitors to the app never
see them.

### How to run it on your own machine

Prerequisite: install `uv` if you don't already have it.

```
$ curl -LsSf https://astral.sh/uv/install.sh | sh
```

1. Sync the dependencies

   ```
   $ uv sync
   ```

2. Run the app

   ```
   $ uv run streamlit run streamlit_app.py
   ```
