import AsyncStorage from '@react-native-async-storage/async-storage';
import { SUPABASE_URL, SUPABASE_ANON_KEY } from './config';

const LOCAL_KEY = 'tiny-steps-data';
const TABLE = 'tiny_steps';
const ROW_ID = 'default';

// Fresh object every call — a shared constant's inner array could be mutated
// and leak stale goals into later "empty" loads.
const empty = () => ({ goals: [] });

const cloudEnabled = () => Boolean(SUPABASE_URL && SUPABASE_ANON_KEY);

const headers = () => ({
  apikey: SUPABASE_ANON_KEY,
  Authorization: `Bearer ${SUPABASE_ANON_KEY}`,
  'Content-Type': 'application/json',
});

async function loadLocal() {
  try {
    const raw = await AsyncStorage.getItem(LOCAL_KEY);
    return raw ? JSON.parse(raw) : empty();
  } catch {
    return empty();
  }
}

async function saveLocal(data) {
  try {
    await AsyncStorage.setItem(LOCAL_KEY, JSON.stringify(data));
  } catch {
    // device storage full or unavailable; nothing sensible to do
  }
}

// Returns { data, cloudError } — cloudError is set when sync is configured
// but unreachable, so the UI can mention it without breaking.
export async function loadData() {
  if (cloudEnabled()) {
    try {
      const url = `${SUPABASE_URL.replace(/\/$/, '')}/rest/v1/${TABLE}?id=eq.${ROW_ID}&select=data`;
      const res = await fetch(url, { headers: headers() });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const rows = await res.json();
      const data = rows.length ? rows[0].data : empty();
      await saveLocal(data);
      return { data, cloudError: null };
    } catch (e) {
      return { data: await loadLocal(), cloudError: String(e) };
    }
  }
  return { data: await loadLocal(), cloudError: null };
}

export async function saveData(data) {
  await saveLocal(data);
  if (!cloudEnabled()) return null;
  try {
    const url = `${SUPABASE_URL.replace(/\/$/, '')}/rest/v1/${TABLE}`;
    const res = await fetch(url, {
      method: 'POST',
      headers: { ...headers(), Prefer: 'resolution=merge-duplicates' },
      body: JSON.stringify([{ id: ROW_ID, data }]),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return null;
  } catch (e) {
    return String(e);
  }
}
