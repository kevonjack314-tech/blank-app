# 🌱 Tiny Steps — mobile app (iOS & Android)

The native mobile version of Tiny Steps, built with [Expo](https://expo.dev)
(React Native). Same goal ladders, same timeline pacing, same daily tasks as
the web app — verified by tests that compare both implementations.

## Try it on your phone right now (free, no store needed)

1. Install [Node.js](https://nodejs.org) (LTS) on your computer.
2. Install the **Expo Go** app on your phone (App Store / Google Play).
3. In this `mobile/` folder run:

   ```
   npm install
   npx expo start
   ```

4. Scan the QR code that appears — iPhone: with the Camera app; Android: with
   Expo Go. The app opens on your phone, and edits reload live.

Progress is saved on the device. To sync with the web app's Supabase database
(so phone and web share one set of goals), open `src/config.js` and paste in
the same `SUPABASE_URL` and anon key you used for the web app.

## Publishing to the App Store / Google Play

Expo's build service (EAS) compiles the store-ready binaries in the cloud —
no Mac or Android Studio required:

1. Create a free account at [expo.dev](https://expo.dev), then:

   ```
   npm install -g eas-cli
   eas login
   eas build:configure
   ```

2. **Google Play** ($25 one-time developer fee):

   ```
   eas build --platform android
   ```

   Upload the resulting `.aab` in the
   [Google Play Console](https://play.google.com/console) (or use
   `eas submit --platform android`).

3. **Apple App Store** ($99/year
   [developer account](https://developer.apple.com)):

   ```
   eas build --platform ios
   eas submit --platform ios
   ```

   Then complete the listing in App Store Connect and submit for review.

Before submitting, add real icon/splash images to `assets/` and reference
them in `app.json` (`icon`, `splash.image`, `android.adaptiveIcon.foregroundImage`) —
stores require them. Expo's docs cover the details:
<https://docs.expo.dev/tutorial/eas/introduction/>.

## Development notes

- `src/goalsLibrary.js` is **generated** from the Python `goals_library.py`
  at the repo root, so the two apps never drift. To regenerate after editing
  the Python file, run from the repo root:

  ```
  python3 -c "
  import json, sys; sys.path.insert(0, '.')
  from goals_library import GOAL_LIBRARY
  body = json.dumps(GOAL_LIBRARY, indent=2, ensure_ascii=False)
  open('mobile/src/goalsLibrary.js', 'w').write(
      '// Generated from goals_library.py — edit that file and re-export to change content.\n'
      'export default ' + body + ';\n')
  "
  ```

- `npm test` runs the logic tests, including a 72-case fixture generated from
  the Python pacing code to guarantee web/mobile parity.
