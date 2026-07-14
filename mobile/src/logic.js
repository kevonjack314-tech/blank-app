// Pure pacing/streak logic shared by all screens. Mirrors streamlit_app.py:
// the timeline maps onto the ladder, so short deadlines climb levels fast and
// long ones linger on each level with smaller steps.

import GOAL_LIBRARY from './goalsLibrary.js';

export { GOAL_LIBRARY };

export const TIMELINE_PRESETS = [
  { label: '2 weeks (sprint)', days: 14 },
  { label: '1 month', days: 30 },
  { label: '2 months', days: 60 },
  { label: '3 months', days: 90 },
  { label: '6 months', days: 180 },
  { label: '1 year (slow & steady)', days: 365 },
];

export function todayISO(now = new Date()) {
  const y = now.getFullYear();
  const m = String(now.getMonth() + 1).padStart(2, '0');
  const d = String(now.getDate()).padStart(2, '0');
  return `${y}-${m}-${d}`;
}

export function addDaysISO(iso, days) {
  const [y, m, d] = iso.split('-').map(Number);
  const dt = new Date(y, m - 1, d + days);
  return todayISO(dt);
}

function daysBetween(fromISO, toISO) {
  const [fy, fm, fd] = fromISO.split('-').map(Number);
  const [ty, tm, td] = toISO.split('-').map(Number);
  const from = new Date(fy, fm - 1, fd);
  const to = new Date(ty, tm - 1, td);
  return Math.round((to - from) / 86400000);
}

// A goal's ladder: its own AI-generated one (built by the web app and synced
// via Supabase) if present, else the library's.
export function levelsFor(goal) {
  return goal.custom_levels || GOAL_LIBRARY[goal.category].levels;
}

export function goalDays(goal, today = todayISO()) {
  const total = Math.max(daysBetween(goal.start_date, goal.end_date), 1);
  const dayIndex = daysBetween(goal.start_date, today); // 0-based, can exceed total
  return { total, dayIndex };
}

export function currentLevelIndex(goal, today = todayISO()) {
  const levels = levelsFor(goal);
  const { total, dayIndex } = goalDays(goal, today);
  const clamped = Math.min(Math.max(dayIndex, 0), total - 1);
  return Math.min(levels.length - 1, Math.floor((clamped * levels.length) / total));
}

// Deterministic daily task: same task all day, variants rotate day to day.
export function taskForDay(goal, levelOffset = 0, today = todayISO()) {
  const levels = levelsFor(goal);
  let lvl = Math.max(0, currentLevelIndex(goal, today) + levelOffset);
  lvl = Math.min(lvl, levels.length - 1);
  const level = levels[lvl];
  const { dayIndex } = goalDays(goal, today);
  const task = level.tasks[Math.max(dayIndex, 0) % level.tasks.length];
  return { levelIndex: lvl, levelTitle: level.title, task };
}

export function paceLabel(totalDays, numLevels) {
  const perLevel = totalDays / numLevels;
  if (perLevel <= 4) {
    return {
      name: '🚀 Accelerated',
      detail: `~${Math.max(1, Math.round(perLevel))} day(s) per level — bigger steps, faster climb`,
    };
  }
  if (perLevel <= 12) {
    return {
      name: '⚡ Steady climb',
      detail: `~${Math.round(perLevel)} days per level — solid daily progress`,
    };
  }
  return {
    name: '🌿 Slow & gradual',
    detail: `~${Math.round(perLevel)} days per level — tiny baby steps with lots of practice`,
  };
}

// Returns { streak, shields }. Streak counts back from today (or yesterday if
// today isn't done yet). Shields protect streaks: every 7 completed tasks
// earns one, and each can auto-cover a single missed day. Two missed days in
// a row always break. Mirrors compute_streak in streamlit_app.py exactly.
export function computeStreak(goal, today = todayISO()) {
  const done = new Set(goal.completed_dates || []);
  const shieldsEarned = Math.floor(done.size / 7);
  let used = 0;
  let day = done.has(today) ? today : addDaysISO(today, -1);
  let streak = 0;
  for (;;) {
    if (done.has(day)) {
      streak += 1;
    } else if (used < shieldsEarned && done.has(addDaysISO(day, -1))) {
      used += 1;
    } else {
      break;
    }
    day = addDaysISO(day, -1);
  }
  return { streak, shields: Math.max(shieldsEarned - used, 0) };
}

export function goalOptions() {
  const items = Object.entries(GOAL_LIBRARY)
    .filter(([key]) => key !== 'custom')
    .map(([key, v]) => ({ key, label: `${v.emoji} ${v.name}` }));
  items.push({ key: 'custom', label: `${GOAL_LIBRARY.custom.emoji} Something else (custom goal)` });
  return items;
}

export function makeGoal({ category, name, days, today = todayISO() }) {
  return {
    id: `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
    category,
    name: name || GOAL_LIBRARY[category].name,
    start_date: today,
    end_date: addDaysISO(today, days),
    completed_dates: [],
  };
}
