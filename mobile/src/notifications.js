// Daily reminder via local scheduled notifications — no server involved, so it
// works offline and in Expo Go. Because tasks are deterministic per date, we
// schedule the next 7 days individually so each notification shows that day's
// ACTUAL task text. The window rolls forward every time the app opens.
// The preference is device-specific and stored separately from goal data.

import AsyncStorage from '@react-native-async-storage/async-storage';
import * as Notifications from 'expo-notifications';
import { Platform } from 'react-native';

import { GOAL_LIBRARY, addDaysISO, taskForDay, todayISO } from './logic';

const PREF_KEY = 'tiny-steps-reminder';
const DAYS_AHEAD = 7;
export const DEFAULT_REMINDER = { enabled: false, hour: 8, minute: 0 };

Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowBanner: true,
    shouldShowList: true,
    shouldPlaySound: false,
    shouldSetBadge: false,
  }),
});

export async function loadReminderPref() {
  try {
    const raw = await AsyncStorage.getItem(PREF_KEY);
    return raw ? { ...DEFAULT_REMINDER, ...JSON.parse(raw) } : { ...DEFAULT_REMINDER };
  } catch {
    return { ...DEFAULT_REMINDER };
  }
}

async function saveReminderPref(pref) {
  try {
    await AsyncStorage.setItem(PREF_KEY, JSON.stringify(pref));
  } catch {
    // non-fatal: the scheduled notifications themselves still exist
  }
}

function bodyFor(goals, dateISO) {
  const active = goals.filter((g) => dateISO <= g.end_date);
  if (active.length === 0) {
    return "One small task today. Open the app to see it — showing up is the whole game.";
  }
  const first = active[0];
  const { task } = taskForDay(first, 0, dateISO);
  const emoji = GOAL_LIBRARY[first.category].emoji;
  let body = active.length > 1 ? `${emoji} ${first.name}: ${task}` : task;
  if (body.length > 170) body = `${body.slice(0, 167)}...`;
  if (active.length > 1) body += ` (+${active.length - 1} more inside)`;
  return body;
}

function fireDate(dateISO, hour, minute) {
  const [y, m, d] = dateISO.split('-').map(Number);
  return new Date(y, m - 1, d, hour, minute, 0, 0);
}

// Returns the pref that actually took effect (enabled=false if permission denied).
export async function applyReminder(pref, goals = []) {
  try {
    await Notifications.cancelAllScheduledNotificationsAsync();
    if (!pref.enabled) {
      await saveReminderPref(pref);
      return pref;
    }

    const perms = await Notifications.requestPermissionsAsync();
    if (!perms.granted && perms.status !== 'granted') {
      const denied = { ...pref, enabled: false };
      await saveReminderPref(denied);
      return denied;
    }

    const channelId = Platform.OS === 'android' ? 'daily-reminder' : undefined;
    if (Platform.OS === 'android') {
      await Notifications.setNotificationChannelAsync('daily-reminder', {
        name: 'Daily reminder',
        importance: Notifications.AndroidImportance.DEFAULT,
      });
    }

    const now = new Date();
    for (let i = 0; i < DAYS_AHEAD; i++) {
      const dateISO = addDaysISO(todayISO(), i);
      const when = fireDate(dateISO, pref.hour, pref.minute);
      if (when <= now) continue; // today's slot already passed
      await Notifications.scheduleNotificationAsync({
        content: {
          title: '🌱 Your tiny step is ready',
          body: bodyFor(goals, dateISO),
        },
        trigger: {
          type: Notifications.SchedulableTriggerInputTypes.DATE,
          date: when,
          channelId,
        },
      });
    }
    await saveReminderPref(pref);
    return pref;
  } catch {
    const failed = { ...pref, enabled: false };
    await saveReminderPref(failed);
    return failed;
  }
}

export function formatTime(hour, minute) {
  const h12 = hour % 12 === 0 ? 12 : hour % 12;
  const ampm = hour < 12 ? 'AM' : 'PM';
  return `${h12}:${String(minute).padStart(2, '0')} ${ampm}`;
}
