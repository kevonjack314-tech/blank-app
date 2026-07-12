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

Progress is saved to a local `user_data.json` next to the app.

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
