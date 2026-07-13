import React, { useEffect, useMemo, useState } from 'react';
import {
  ActivityIndicator,
  Alert,
  SafeAreaView,
  ScrollView,
  StatusBar,
  StyleSheet,
  Switch,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from 'react-native';

import {
  GOAL_LIBRARY,
  TIMELINE_PRESETS,
  computeStreak,
  currentLevelIndex,
  goalDays,
  goalOptions,
  makeGoal,
  paceLabel,
  taskForDay,
  todayISO,
  addDaysISO,
} from './src/logic';
import { loadData, saveData } from './src/storage';
import { applyReminder, formatTime, loadReminderPref } from './src/notifications';

const C = {
  bg: '#f4f7f4',
  card: '#ffffff',
  ink: '#1c2b21',
  sub: '#5c6f63',
  accent: '#2e7d4f',
  accentSoft: '#e3f2e9',
  warn: '#8a6d1a',
  warnSoft: '#fdf3d7',
  line: '#e2e8e3',
  danger: '#b3402f',
};

export default function App() {
  const [data, setData] = useState(null);
  const [screen, setScreen] = useState({ name: 'home' });
  const [cloudNote, setCloudNote] = useState(null);

  useEffect(() => {
    loadData().then(({ data: d, cloudError }) => {
      setData(d);
      if (cloudError) setCloudNote('Cloud sync unreachable — using data saved on this device.');
    });
  }, []);

  const persist = async (next) => {
    setData(next);
    const err = await saveData(next);
    if (err) setCloudNote('Saved on device, but cloud sync failed. Will retry on your next check-in.');
  };

  if (!data) {
    return (
      <SafeAreaView style={[styles.screen, styles.center]}>
        <ActivityIndicator size="large" color={C.accent} />
      </SafeAreaView>
    );
  }

  const goHome = () => setScreen({ name: 'home' });
  const props = { data, persist, setScreen, goHome, cloudNote };

  return (
    <SafeAreaView style={styles.screen}>
      <StatusBar barStyle="dark-content" backgroundColor={C.bg} />
      {screen.name === 'add' || data.goals.length === 0 ? (
        <AddGoalScreen {...props} firstGoal={data.goals.length === 0} />
      ) : screen.name === 'goal' ? (
        <GoalScreen {...props} goalId={screen.goalId} />
      ) : (
        <HomeScreen {...props} />
      )}
    </SafeAreaView>
  );
}

function Header({ title, subtitle, onBack }) {
  return (
    <View style={styles.header}>
      {onBack ? (
        <TouchableOpacity onPress={onBack} style={styles.backBtn} hitSlop={{ top: 12, bottom: 12, left: 12, right: 12 }}>
          <Text style={styles.backTxt}>‹ Back</Text>
        </TouchableOpacity>
      ) : null}
      <Text style={styles.h1}>{title}</Text>
      {subtitle ? <Text style={styles.sub}>{subtitle}</Text> : null}
    </View>
  );
}

function HomeScreen({ data, setScreen, cloudNote }) {
  const today = todayISO();
  const doneCount = data.goals.filter((g) => (g.completed_dates || []).includes(today)).length;
  const allDone = doneCount === data.goals.length;

  return (
    <ScrollView contentContainerStyle={styles.content}>
      <Header
        title="🌱 Tiny Steps"
        subtitle={
          allDone
            ? `All ${data.goals.length} task(s) done today. Rest easy — you earned it. 😌`
            : `✅ ${doneCount} of ${data.goals.length} tasks done today`
        }
      />
      {cloudNote ? <Note text={cloudNote} /> : null}
      {data.goals.map((g) => {
        const lib = GOAL_LIBRARY[g.category];
        const done = (g.completed_dates || []).includes(today);
        const { total, dayIndex } = goalDays(g);
        const streak = computeStreak(g);
        return (
          <TouchableOpacity key={g.id} style={styles.card} onPress={() => setScreen({ name: 'goal', goalId: g.id })}>
            <View style={styles.rowBetween}>
              <Text style={styles.cardTitle}>
                {lib.emoji} {g.name}
              </Text>
              <Text style={{ fontSize: 20 }}>{done ? '✅' : '📌'}</Text>
            </View>
            <Text style={styles.cardMeta}>
              Day {Math.min(dayIndex + 1, total)} of {total} · 🔥 {streak} streak
            </Text>
            <ProgressBar pct={Math.min(Math.max(dayIndex, 0) / total, 1)} />
            <Text style={styles.cardHint}>{done ? 'Done for today — tap to review' : "Tap for today's tiny step"}</Text>
          </TouchableOpacity>
        );
      })}
      <TouchableOpacity style={styles.secondaryBtn} onPress={() => setScreen({ name: 'add' })}>
        <Text style={styles.secondaryTxt}>➕ Work on something else too</Text>
      </TouchableOpacity>
      <ReminderCard />
    </ScrollView>
  );
}

function ReminderCard() {
  const [pref, setPref] = useState(null);

  useEffect(() => {
    loadReminderPref().then(setPref);
  }, []);

  if (!pref) return null;

  const apply = async (next) => {
    setPref(next); // optimistic, then reconcile with what actually took effect
    const effective = await applyReminder(next);
    setPref(effective);
    if (next.enabled && !effective.enabled) {
      Alert.alert(
        'Notifications are off',
        'Tiny Steps needs notification permission for reminders. You can enable it in your phone Settings.'
      );
    }
  };

  const shiftTime = (deltaMinutes) => {
    const totalMin = (pref.hour * 60 + pref.minute + deltaMinutes + 1440) % 1440;
    apply({ ...pref, hour: Math.floor(totalMin / 60), minute: totalMin % 60 });
  };

  return (
    <View style={styles.card}>
      <View style={styles.rowBetween}>
        <Text style={styles.cardTitle}>⏰ Daily reminder</Text>
        <Switch
          value={pref.enabled}
          onValueChange={(on) => apply({ ...pref, enabled: on })}
          trackColor={{ true: C.accent }}
        />
      </View>
      {pref.enabled ? (
        <View style={[styles.rowBetween, { marginTop: 12 }]}>
          <TouchableOpacity style={styles.timeBtn} onPress={() => shiftTime(-30)}>
            <Text style={styles.timeBtnTxt}>−30 min</Text>
          </TouchableOpacity>
          <Text style={styles.timeTxt}>{formatTime(pref.hour, pref.minute)}</Text>
          <TouchableOpacity style={styles.timeBtn} onPress={() => shiftTime(30)}>
            <Text style={styles.timeBtnTxt}>+30 min</Text>
          </TouchableOpacity>
        </View>
      ) : (
        <Text style={styles.cardHint}>Get a gentle nudge each day when your tiny step is ready.</Text>
      )}
    </View>
  );
}

function GoalScreen({ data, persist, goHome, goalId }) {
  const goal = data.goals.find((g) => g.id === goalId);
  const [easier, setEasier] = useState(false);
  if (!goal) {
    goHome();
    return null;
  }

  const lib = GOAL_LIBRARY[goal.category];
  const today = todayISO();
  const { total, dayIndex } = goalDays(goal);
  const doneToday = (goal.completed_dates || []).includes(today);
  const finished = dayIndex >= total;
  const streak = computeStreak(goal);
  const levels = lib.levels;
  const lvlNow = currentLevelIndex(goal);
  const { levelIndex, levelTitle, task } = taskForDay(goal, easier ? -1 : 0);
  const pace = paceLabel(total, levels.length);
  const pct = Math.min(Math.max(dayIndex, 0) / total, 1);

  const update = (fn) => {
    const next = { ...data, goals: data.goals.map((g) => (g.id === goal.id ? fn({ ...g }) : g)) };
    persist(next);
  };
  const removeGoal = () => {
    persist({ ...data, goals: data.goals.filter((g) => g.id !== goal.id) });
    goHome();
  };

  return (
    <ScrollView contentContainerStyle={styles.content}>
      <Header title={`${lib.emoji} ${goal.name}`} onBack={goHome} />

      <View style={styles.metricsRow}>
        <Metric label="Day" value={`${Math.min(dayIndex + 1, total)} / ${total}`} />
        <Metric label="Streak" value={`🔥 ${streak}`} />
        <Metric label="Done" value={`${(goal.completed_dates || []).length}`} />
      </View>
      <ProgressBar pct={pct} />
      <Text style={styles.cardMeta}>{Math.round(pct * 100)}% through your timeline</Text>

      {lib.support_note ? <Note text={`💛 ${lib.support_note}`} /> : null}

      {finished ? (
        <>
          <View style={[styles.card, { backgroundColor: C.accentSoft }]}>
            <Text style={styles.cardTitle}>🎉 You made it to the end of your {total}-day journey!</Text>
            <Text style={styles.cardBody}>
              You completed {(goal.completed_dates || []).length} daily tasks. Look how far you've come.
            </Text>
          </View>
          <TouchableOpacity
            style={styles.primaryBtn}
            onPress={() => update((g) => ({ ...g, end_date: addDaysISO(g.end_date, 30) }))}
          >
            <Text style={styles.primaryTxt}>Keep going — extend 30 days</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.secondaryBtn} onPress={removeGoal}>
            <Text style={styles.secondaryTxt}>Finish & remove this goal</Text>
          </TouchableOpacity>
        </>
      ) : (
        <>
          <Text style={styles.levelLine}>
            Level {levelIndex + 1} of {levels.length}: {levelTitle} · {pace.name}
          </Text>
          {easier ? <Text style={styles.cardHint}>A gentler step from the previous level — still counts. 💚</Text> : null}

          {doneToday ? (
            <View style={[styles.card, { backgroundColor: C.accentSoft }]}>
              <Text style={styles.cardTitle}>✅ Done for today!</Text>
              <Text style={styles.cardBody}>You showed up. That's the whole game.</Text>
            </View>
          ) : (
            <>
              <View style={[styles.card, styles.taskCard]}>
                <Text style={styles.taskLabel}>📌 TODAY'S TINY STEP</Text>
                <Text style={styles.taskTxt}>{task}</Text>
              </View>
              <TouchableOpacity
                style={styles.primaryBtn}
                onPress={() => {
                  setEasier(false);
                  update((g) => ({ ...g, completed_dates: [...(g.completed_dates || []), today] }));
                }}
              >
                <Text style={styles.primaryTxt}>I did it ✅</Text>
              </TouchableOpacity>
              {lvlNow > 0 && !easier ? (
                <TouchableOpacity style={styles.secondaryBtn} onPress={() => setEasier(true)}>
                  <Text style={styles.secondaryTxt}>Too big today — give me a smaller step</Text>
                </TouchableOpacity>
              ) : null}
            </>
          )}

          <Text style={styles.sectionTitle}>🪜 Your ladder</Text>
          <View style={styles.card}>
            {levels.map((lvl, i) => (
              <Text
                key={lvl.title}
                style={[
                  styles.ladderRow,
                  i === lvlNow && styles.ladderNow,
                  i < lvlNow && styles.ladderDone,
                ]}
              >
                {i < lvlNow ? '✅' : i === lvlNow ? '➡️' : '🔒'} Level {i + 1}: {lvl.title}
                {i === lvlNow ? '  ← you are here' : ''}
              </Text>
            ))}
          </View>

          <Text style={styles.cardMeta}>
            Started {goal.start_date} · target {goal.end_date} · {Math.max(total - dayIndex, 0)} days left
          </Text>
          <TouchableOpacity
            style={[styles.secondaryBtn, { borderColor: C.danger }]}
            onPress={() =>
              Alert.alert('Delete this goal?', 'Your progress on it will be lost.', [
                { text: 'Cancel', style: 'cancel' },
                { text: 'Delete', style: 'destructive', onPress: removeGoal },
              ])
            }
          >
            <Text style={[styles.secondaryTxt, { color: C.danger }]}>Delete this goal</Text>
          </TouchableOpacity>
        </>
      )}
    </ScrollView>
  );
}

function AddGoalScreen({ data, persist, goHome, firstGoal }) {
  const options = useMemo(goalOptions, []);
  const [category, setCategory] = useState(options[0].key);
  const [customName, setCustomName] = useState('');
  const [presetIdx, setPresetIdx] = useState(2); // default: 2 months
  const [customDays, setCustomDays] = useState('');

  const days = presetIdx === -1 ? Math.max(parseInt(customDays, 10) || 0, 0) : TIMELINE_PRESETS[presetIdx].days;
  const numLevels = GOAL_LIBRARY[category].levels.length;
  const pace = days >= 7 ? paceLabel(days, numLevels) : null;

  const start = () => {
    if (category === 'custom' && !customName.trim()) {
      Alert.alert('Almost there', 'Give your custom goal a name first.');
      return;
    }
    if (days < 7) {
      Alert.alert('Timeline too short', 'Give yourself at least 7 days.');
      return;
    }
    const goal = makeGoal({ category, name: category === 'custom' ? customName.trim() : null, days });
    persist({ ...data, goals: [...data.goals, goal] });
    goHome();
  };

  return (
    <ScrollView contentContainerStyle={styles.content}>
      <Header
        title={firstGoal ? '🌱 Tiny Steps' : '➕ New goal'}
        subtitle={
          firstGoal
            ? "Pick something you want to get better at. Every day you'll get one small task — the size of the steps depends on how much time you give yourself."
            : null
        }
        onBack={firstGoal ? null : goHome}
      />

      <Text style={styles.sectionTitle}>What do you want to improve?</Text>
      {options.map((o) => (
        <TouchableOpacity
          key={o.key}
          style={[styles.choice, category === o.key && styles.choiceOn]}
          onPress={() => setCategory(o.key)}
        >
          <Text style={[styles.choiceTxt, category === o.key && styles.choiceTxtOn]}>{o.label}</Text>
          {category === o.key && o.key !== 'custom' ? (
            <Text style={styles.choiceDesc}>{GOAL_LIBRARY[o.key].description}</Text>
          ) : null}
        </TouchableOpacity>
      ))}
      {category === 'custom' ? (
        <TextInput
          style={styles.input}
          placeholder="e.g. Learn guitar, wake up earlier, save money..."
          placeholderTextColor={C.sub}
          value={customName}
          onChangeText={setCustomName}
        />
      ) : null}

      <Text style={styles.sectionTitle}>How long do you want to give yourself?</Text>
      <Text style={styles.cardHint}>
        This matters: 2 months means bigger steps and a faster climb. A year means slower, gentler baby steps with
        more practice at each stage.
      </Text>
      {TIMELINE_PRESETS.map((p, i) => (
        <TouchableOpacity key={p.label} style={[styles.choice, presetIdx === i && styles.choiceOn]} onPress={() => setPresetIdx(i)}>
          <Text style={[styles.choiceTxt, presetIdx === i && styles.choiceTxtOn]}>{p.label}</Text>
        </TouchableOpacity>
      ))}
      <TouchableOpacity style={[styles.choice, presetIdx === -1 && styles.choiceOn]} onPress={() => setPresetIdx(-1)}>
        <Text style={[styles.choiceTxt, presetIdx === -1 && styles.choiceTxtOn]}>Custom...</Text>
        {presetIdx === -1 ? (
          <TextInput
            style={styles.input}
            placeholder="Number of days (e.g. 45)"
            placeholderTextColor={C.sub}
            keyboardType="number-pad"
            value={customDays}
            onChangeText={setCustomDays}
          />
        ) : null}
      </TouchableOpacity>

      {pace ? (
        <View style={[styles.card, { backgroundColor: C.accentSoft }]}>
          <Text style={styles.cardTitle}>{pace.name}</Text>
          <Text style={styles.cardBody}>
            {days} days across {numLevels} levels. {pace.detail}.
          </Text>
        </View>
      ) : null}

      <TouchableOpacity style={styles.primaryBtn} onPress={start}>
        <Text style={styles.primaryTxt}>Start this journey 🌱</Text>
      </TouchableOpacity>
    </ScrollView>
  );
}

function Metric({ label, value }) {
  return (
    <View style={styles.metric}>
      <Text style={styles.metricLabel}>{label}</Text>
      <Text style={styles.metricValue}>{value}</Text>
    </View>
  );
}

function ProgressBar({ pct }) {
  return (
    <View style={styles.barTrack}>
      <View style={[styles.barFill, { width: `${Math.round(pct * 100)}%` }]} />
    </View>
  );
}

function Note({ text }) {
  return (
    <View style={[styles.card, { backgroundColor: C.warnSoft }]}>
      <Text style={[styles.cardBody, { color: C.warn }]}>{text}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: C.bg },
  center: { justifyContent: 'center', alignItems: 'center' },
  content: { padding: 20, paddingBottom: 48 },
  header: { marginBottom: 12 },
  backBtn: { marginBottom: 8, alignSelf: 'flex-start' },
  backTxt: { color: C.accent, fontSize: 16, fontWeight: '600' },
  h1: { fontSize: 26, fontWeight: '800', color: C.ink },
  sub: { fontSize: 15, color: C.sub, marginTop: 6, lineHeight: 21 },
  sectionTitle: { fontSize: 17, fontWeight: '700', color: C.ink, marginTop: 18, marginBottom: 8 },
  card: {
    backgroundColor: C.card,
    borderRadius: 14,
    padding: 16,
    marginVertical: 8,
    borderWidth: 1,
    borderColor: C.line,
  },
  rowBetween: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  cardTitle: { fontSize: 17, fontWeight: '700', color: C.ink },
  cardBody: { fontSize: 15, color: C.ink, marginTop: 6, lineHeight: 21 },
  cardMeta: { fontSize: 13, color: C.sub, marginTop: 6 },
  cardHint: { fontSize: 13, color: C.sub, marginTop: 8, lineHeight: 18 },
  taskCard: { backgroundColor: '#eef6ff', borderColor: '#d3e5f8' },
  taskLabel: { fontSize: 12, fontWeight: '800', color: '#2b5c8a', letterSpacing: 1 },
  taskTxt: { fontSize: 17, color: C.ink, marginTop: 8, lineHeight: 24 },
  levelLine: { fontSize: 14, fontWeight: '600', color: C.ink, marginTop: 12 },
  metricsRow: { flexDirection: 'row', gap: 8, marginVertical: 8 },
  metric: {
    flex: 1,
    backgroundColor: C.card,
    borderRadius: 12,
    paddingVertical: 10,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: C.line,
  },
  metricLabel: { fontSize: 12, color: C.sub },
  metricValue: { fontSize: 16, fontWeight: '700', color: C.ink, marginTop: 2 },
  barTrack: { height: 10, backgroundColor: C.line, borderRadius: 5, marginTop: 8, overflow: 'hidden' },
  barFill: { height: '100%', backgroundColor: C.accent, borderRadius: 5 },
  primaryBtn: {
    backgroundColor: C.accent,
    borderRadius: 14,
    paddingVertical: 15,
    alignItems: 'center',
    marginTop: 12,
  },
  primaryTxt: { color: '#fff', fontSize: 17, fontWeight: '700' },
  secondaryBtn: {
    borderWidth: 1.5,
    borderColor: C.accent,
    borderRadius: 14,
    paddingVertical: 13,
    alignItems: 'center',
    marginTop: 10,
    backgroundColor: C.card,
  },
  secondaryTxt: { color: C.accent, fontSize: 15, fontWeight: '600' },
  choice: {
    backgroundColor: C.card,
    borderRadius: 12,
    padding: 14,
    marginVertical: 4,
    borderWidth: 1.5,
    borderColor: C.line,
  },
  choiceOn: { borderColor: C.accent, backgroundColor: C.accentSoft },
  choiceTxt: { fontSize: 15, color: C.ink, fontWeight: '500' },
  choiceTxtOn: { fontWeight: '700', color: C.accent },
  choiceDesc: { fontSize: 13, color: C.sub, marginTop: 6, lineHeight: 18 },
  ladderRow: { fontSize: 14, color: C.sub, paddingVertical: 5 },
  ladderNow: { color: C.ink, fontWeight: '700' },
  ladderDone: { color: C.accent },
  timeBtn: {
    backgroundColor: C.accentSoft,
    borderRadius: 10,
    paddingVertical: 8,
    paddingHorizontal: 14,
  },
  timeBtnTxt: { color: C.accent, fontWeight: '700', fontSize: 14 },
  timeTxt: { fontSize: 20, fontWeight: '800', color: C.ink },
  input: {
    backgroundColor: C.card,
    borderWidth: 1.5,
    borderColor: C.line,
    borderRadius: 12,
    padding: 12,
    fontSize: 15,
    color: C.ink,
    marginTop: 8,
  },
});
