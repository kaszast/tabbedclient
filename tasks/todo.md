# Feladatok: Univerzális Multi-Tab Web Kliens (Rambox alternatíva)

## 1. Követelményfeltárás és technológiai egyeztetés
- [x] Platform-korlátok tisztázása: TUI elhagyva, fókusz a grafikus platformokon (Linux, Windows, Android)
- [x] Keretrendszer kiválasztása: Tauri v2 (Rust backend + TypeScript/HTML/CSS frontend) jóváhagyva
- [x] Funkcionális követelmények rögzítése:
  - Fülek és munkamenetek: Fülönkénti/profilonkénti izoláció (multi-account, különálló cookie jar / data directory)
  - Fülkezelés: Beépített grafikus szerkesztőfelület, előre definiált gyorsgombok (pl. WhatsApp, Gmail, Slack, Telegram stb.) + tetszőleges egyedi URL, név és profilazonosító megadásával
  - Konfiguráció: Helyi JSON fájl, nulla külső hálózati kommunikáció / telemetria
  - Vertikális fülelrendezés desktopon és mobilon
- [x] Rendszerértesítések és badge jelzések kezelése:
  - Fülönkénti olvasatlan számláló / állapotjelző pötty a vertikális fülsávban
  - Natív értesítések továbbítása a háttérben lévő fülekről
- [x] Rendszertálca (System Tray / App Indicator) és háttérben futás:
  - Bezáráskor (X) minimalizálás a rendszertálcára
  - Tálcamenü: Ablak megjelenítése / elrejtése, végleges kilépés
- [x] Mobil (Android) felület viselkedése:
  - Asztali nézetben állandó bal oldali vertikális sáv
  - Mobilon összecsukódó, érintéssel/gombbal előhívható fiók (Drawer)
- [x] Adatvédelmi és biztonsági kör: Indulásnál elegendő a tiszta helyi tárolás (standard local config + platform natív webview adatmappák), nincs szükség induláskor PIN-re vagy titkosításra.

## 2. Architektúra és tervezés
- [x] Részletes architektúra és adatfolyam specifikáció elkészítése (`docs/spec.md`)
- [x] 10 professzionális képernyőterv bemutatása, jóváhagyott témák kiválasztva:
  - 1. Slate Studio (Sötét)
  - 2. Nordic Crisp (Világos)
  - 3. JetBrains Obsidian (Sötét mérnöki)
  - 8. Solarized Paper (Világos szépia)
  - 10. Enterprise Cobalt (Világos vállalati)
  - Témaváltás perzisztálása helyi konfigurációban
  - Asztali összecsukható (compact / icon-only) vertikális sáv támogatása

## 3. Implementáció
- [x] UI és moduláris frontend réteg kialakítása
  - [x] HTML keretrendszer: vertikális fülsáv (összecsukható), webview nézet, sablon modál és beállítások (`src/index.html`)
  - [x] 5 téma CSS implementációja (Slate, Nordic, JetBrains, Solarized, Enterprise) és kompakt mód stílusok (`src/styles.css`)
  - [x] Alkalmazáslogika: Témakezelő, Fülkezelő, Profil/Partíció kezelő, Értesítési híd (`src/app.js`)
  - [x] Alapértelmezett konfiguráció és sablonok (`src/config.js`)
- [x] Backend és integrációs réteg
  - [x] Tauri v2 konfiguráció és projektstruktúra (`src-tauri/tauri.conf.json`, `Cargo.toml`, `src-tauri/src/main.rs`)
  - [x] Linux WebKitGTK multi-account futtató modul (`desktop/tabbedclient.py`)
- [x] Automatizált tesztek
  - [x] Konfiguráció, fülkezelési és tématesztek (`tests/test_tabs.js`, `tests/test_themes.js`)

## 4. Validáció és tesztelés
- [x] Tesztek futtatása és ellenőrzése (`npm test` sikeres, zöld)
- [x] Asztali és mobil integráció ellenőrzése, dokumentáció (`docs/BUILD_GUIDE.md`)

## 5. Review és hibajavítások (2026-10-23)
- [x] Egységteszt mock javítás a `tests/test_tabs.js`-ben (`querySelector: () => dummyEl()`)
- [x] Rendszertálca (AyatanaAppIndicator3) és háttérműködés implementálása a `desktop/tabbedclient.py`-ban
- [x] HTML5 `show-notification` és `notify::title` olvasatlan számláló / badge integráció
- [x] Biztonságos jogosultságkezelés a `desktop/tabbedclient.py`-ban (`_on_permission_request`)
- [x] Fülek sorrendezésének és fülönkénti értesítés-némításnak a megvalósítása (kontextusmenü + irányítópult)
- [x] Specifikáció szerinti sablonok (9 db) és konfigurációs séma konszolidálása (`src/config.js`, `src/welcome.html`)
- [x] Tauri ikonok és perzisztens konfigurációkezelés (`src-tauri/icons/`, `src-tauri/src/main.rs`)
- [x] Végrehajtható és telepíthető csomagok előállítása Linux (.deb + .tar.gz) és Windows (.zip) platformra (`npm run build:packages`)
- [x] Külső hivatkozások kezelése: `target="_blank"`, `window.open` és külső domainek (pl. Gmail "View in browser", hírlevél linkek) megnyitása a rendszer alapértelmezett böngészőjében (`_on_decide_policy`, `_on_create_webview`)
- [x] Fül-ikonok méretének 2x-esre növelése (16px -> 32px, faviconek és SVG-k, 40px konténer) mind normál, mind összecsukott oldalsávban (`src/styles.css`, `src/sidebar.html`, `tests/test_themes.js`)
- [x] 8 darab hivatalos ikon terv elkészítése (`resources/icons/`), felhasználói kiválasztás (5. Bento Multi-Grid) és teljes körű rendszer-integrációja (asztali indító, tray, webes címsor, többféle felbontású PNG/ICO/SVG és telepítőcsomagok)
- [x] Zorin OS / GNOME tálca- és asztali integráció javítása: `set_default_icon_list` többméretes X11 `_NET_WM_ICON` regisztráció, `StartupWMClass=tabbedclient` egyezés, automatikus `~/.local/share/applications` launcher regisztráció és `install_desktop_entry.sh` eszköz, Debian csomag `postinst`/`postrm` gyorsítótár-frissítésekkel
- [x] Debian (.deb) csomagfuttatási hiba és jogosultságkezelés elhárítása: XDG Base Directory specifikáció (`~/.config/tabbedclient` és `~/.local/share/tabbedclient`) bevezetése a `/usr/share/tabbedclient` alatti PermissionError ellen, deprecated `set_wmclass` figyelmeztetés megszüntetése, frissített csomagok újraépítése.
