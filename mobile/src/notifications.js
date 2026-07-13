// Daily reminder via local scheduled notifications — no server involved, so it
// works offline and in Expo Go. The preference is device-specific and stored
// separately from goal data (it shouldn't sync between devices).

import AsyncStorage from '@react-native-async-storage/async-storage';
import * as Notifications from 'expo-notifications';
import { Platform } from 'react-native';

const PREF_KEY = 'tiny-steps-reminder';
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
    // non-fatal: the scheduled notification itself still exists
  }
}

// Returns the pref that actually took effect (enabled=false if permission denied).
export async function applyReminder(pref) {
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

    if (Platform.OS === 'android') {
      await Notifications.setNotificationChannelAsync('daily-reminder', {
        name: 'Daily reminder',
        importance: Notifications.AndroidImportance.DEFAULT,
      });
    }

    await Notifications.scheduleNotificationAsync({
      content: {
        title: '🌱 Your tiny step is ready',
        body: "One small task today. Open the app to see it — showing up is the whole game.",
      },
      trigger: {
        type: Notifications.SchedulableTriggerInputTypes.DAILY,
        hour: pref.hour,
        minute: pref.minute,
        channelId: Platform.OS === 'android' ? 'daily-reminder' : undefined,
      },
    });
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
