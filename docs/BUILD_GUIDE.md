# TabbedClient - Építési és Futtatási Útmutató (Linux, Windows, Android)

Ez a dokumentum bemutatja, hogyan futtatható és fordítható a TabbedClient az egyes célplatformokra.

---

## 1. Azonnali Futtatás Linuxon (Natív GTK3 + WebKitGTK)

A projekt tartalmaz egy beépített natív futtatót, amely külső npm és rustup telepítés nélkül, közvetlenül a rendszerben már meglévő WebKitGTK és Python GObject környezetet használja.

### Indítás:
```bash
npm start
# vagy közvetlenül:
python3 desktop/tabbedclient.py
```

### Rendszerkövetelmények (Debian/Ubuntu):
```bash
sudo apt update
sudo apt install -y python3-gi gir1.2-gtk-3.0 gir1.2-webkit2-4.1 gir1.2-ayatanaappindicator3-0.1 gir1.2-notify-0.7
```

---

## 1.1. Kész Csomagok Előállítása (Linux & Windows)

A beépített csomagoló script automatikusan elkészíti a végrehajtható telepítő- és hordozható csomagokat:

```bash
npm run build:packages
# vagy:
python3 scripts/build_packages.py
```

### Elkészült csomagok a `dist/` mappában:
- **`dist/tabbedclient_1.0.0_all.deb`**: Natív Debian/Ubuntu/Mint telepítőcsomag, amely elhelyezi a binárist (`/usr/bin/tabbedclient`), az asztali indítóikont és a menübejegyzést. Telepítés: `sudo dpkg -i dist/tabbedclient_1.0.0_all.deb`.
- **`dist/tabbedclient-1.0.0-linux-x86_64.tar.gz`**: Független, telepítés nélkül közvetlenül futtatható hordozható Linux csomag (`./tabbedclient`).
- **`dist/tabbedclient-1.0.0-windows.zip`**: Önálló hordozható Windows csomag, amely dupla kattintással futtatható a `TabbedClient.vbs` (ablakmentes) vagy `TabbedClient.bat` segítségével, automatikus Microsoft Edge App Mode és elszeparált adatprofil-támogatással.

---

## 2. Asztali Fordítás Tauri v2-vel (Linux & Windows)

A Tauri v2 minimális erőforrás-igényű natív futtatható állományokat (`.deb`, `.AppImage`, Windows `.msi` / `.exe`) készít.

### 2.1. Rust Toolchain Telepítése:
```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source "$HOME/.cargo/env"
```

### 2.2. Linux Asztali Függőségek:
```bash
sudo apt install -y libwebkit2gtk-4.1-dev build-essential curl wget file libssl-dev libgtk-3-dev libayatana-appindicator3-dev librsvg2-dev
```

### 2.3. Asztali Építés:
```bash
cargo install tauri-cli --version "^2.0.0"
cargo tauri build
```
A kész bináris a `src-tauri/target/release/bundle/` könyvtárban található.

---

## 3. Mobil Építés (Android)

A Tauri v2 hivatalosan támogatja az Android platformot az Android System WebView-ra támaszkodva.

### 3.1. Szükséges Eszközök:
- **Android Studio** (vagy parancssori Android SDK és NDK r25+)
- Környezeti változók:
  ```bash
  export ANDROID_HOME="$HOME/Android/Sdk"
  export NDK_HOME="$ANDROID_HOME/ndk/25.2.9519653"
  ```
- Rust Android célarchitektúrák:
  ```bash
  rustup target add aarch64-linux-android armv7-linux-androideabi i686-linux-android x86_64-linux-android
  ```

### 3.2. Android Projekt Inicializálása és Futtatása:
```bash
cargo tauri android init
cargo tauri android dev
```

### 3.3. APK / AAB Generálás:
```bash
cargo tauri android build --apk
```
A generált telepítőfájl: `src-tauri/gen/android/app/build/outputs/apk/universal/release/app-universal-release-unsigned.apk`.

---

## 4. Tesztelés

Az egységtesztek (konfiguráció, fülkezelés, 5 jóváhagyott téma megléte és CSS definíciók) a beépített Node.js környezettel futtathatók:
```bash
npm test
```

---

## 5. Adatvédelem és Partíciók

- **Zero-Telemetry:** Az alkalmazás forráskódja nem tartalmaz külső szerverre mutató analitikai vagy mérési hívást.
- **Munkamenet-adatok helye:** A felhasználói adatok (cookie-k, helyi tárolók, profilok) a `data/profiles/<profil_id>/` könyvtárban élnek teljesen elszeparálva.
