import assert from 'node:assert/strict';
import test from 'node:test';
import { readFileSync } from 'node:fs';

import {
  GOAL_LIBRARY,
  addDaysISO,
  computeStreak,
  currentLevelIndex,
  levelsFor,
  makeGoal,
  paceLabel,
  taskForDay,
} from '../src/logic.js';

const fixture = JSON.parse(readFileSync(new URL('./pacing_fixture.json', import.meta.url), 'utf8'));
const shieldsFixture = JSON.parse(
  readFileSync(new URL('./shields_fixture.json', import.meta.url), 'utf8')
);

const START = '2026-01-01';
const goalFor = (category, total) => ({
  category,
  start_date: START,
  end_date: addDaysISO(START, total),
  completed_dates: [],
});

test('pacing matches the Python web app exactly', () => {
  for (const c of fixture) {
    const goal = goalFor(c.category, c.total);
    const today = addDaysISO(START, c.dayIndex);
    assert.equal(
      currentLevelIndex(goal, today),
      c.expectedLevel,
      `${c.category} total=${c.total} day=${c.dayIndex}`
    );
  }
});

test('2-month plan outpaces 1-year plan at day 30', () => {
  const today = addDaysISO(START, 30);
  const fast = currentLevelIndex(goalFor('singing', 60), today);
  const slow = currentLevelIndex(goalFor('singing', 365), today);
  assert.ok(fast > slow, `fast=${fast} slow=${slow}`);
});

test('task is deterministic within a day and rotates across days', () => {
  const goal = goalFor('reading', 60);
  const today = addDaysISO(START, 10);
  const a = taskForDay(goal, 0, today);
  const b = taskForDay(goal, 0, today);
  assert.equal(a.task, b.task);
  const tomorrow = taskForDay(goal, 0, addDaysISO(START, 11));
  assert.notEqual(a.task, tomorrow.task);
});

test('easier step drops one level but never below zero', () => {
  const goal = goalFor('fitness', 60);
  const today = addDaysISO(START, 30);
  const normal = taskForDay(goal, 0, today);
  const easier = taskForDay(goal, -1, today);
  assert.equal(easier.levelIndex, normal.levelIndex - 1);
  const day0 = taskForDay(goal, -1, START);
  assert.equal(day0.levelIndex, 0);
});

test('streaks count consecutive days, forgiving an unfinished today', () => {
  const today = '2026-03-10';
  const g = (dates) => ({ category: 'reading', completed_dates: dates });
  assert.equal(computeStreak(g([]), today).streak, 0);
  assert.equal(computeStreak(g(['2026-03-09', '2026-03-10']), today).streak, 2);
  assert.equal(computeStreak(g(['2026-03-08', '2026-03-09']), today).streak, 2); // today not done yet
  assert.equal(computeStreak(g(['2026-03-06', '2026-03-09']), today).streak, 1); // gap resets
});

test('streak shields match the Python web app exactly', () => {
  for (const c of shieldsFixture) {
    const { streak, shields } = computeStreak(
      { category: 'reading', completed_dates: c.completedDates },
      c.today
    );
    assert.equal(streak, c.expectedStreak, `${c.name}: streak`);
    assert.equal(shields, c.expectedShields, `${c.name}: shields`);
  }
});

test('AI custom ladders override the library ladder', () => {
  const customLevels = [
    { title: 'Warmup', tasks: ['Juggle 1 ball for 2 minutes', 'Toss and catch 10 times'] },
    { title: 'Two balls', tasks: ['Exchange two balls 10 times', 'Two-ball cascade for 1 minute'] },
  ];
  const goal = {
    category: 'custom',
    custom_levels: customLevels,
    start_date: '2026-01-01',
    end_date: addDaysISO('2026-01-01', 60),
    completed_dates: [],
  };
  assert.equal(levelsFor(goal), customLevels);
  const late = taskForDay(goal, 0, addDaysISO('2026-01-01', 45));
  assert.equal(late.levelTitle, 'Two balls');
  assert.ok(customLevels[1].tasks.includes(late.task));
  delete goal.custom_levels;
  assert.equal(levelsFor(goal), GOAL_LIBRARY.custom.levels);
});

test('pace labels match web thresholds', () => {
  assert.equal(paceLabel(14, 7).name, '🚀 Accelerated');
  assert.equal(paceLabel(60, 7).name, '⚡ Steady climb');
  assert.equal(paceLabel(365, 7).name, '🌿 Slow & gradual');
});

test('makeGoal builds a valid goal with the right end date', () => {
  const g = makeGoal({ category: 'singing', name: null, days: 60, today: START });
  assert.equal(g.name, GOAL_LIBRARY.singing.name);
  assert.equal(g.end_date, '2026-03-02');
  assert.deepEqual(g.completed_dates, []);
});

test('library content is intact for every category', () => {
  for (const [key, area] of Object.entries(GOAL_LIBRARY)) {
    assert.ok(area.levels.length >= 7, key);
    for (const level of area.levels) {
      assert.ok(level.title && level.tasks.length >= 2, `${key}/${level.title}`);
    }
  }
});
