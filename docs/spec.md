# TabbedClient - Rendszer- és Architektúra Specifikáció

## 1. Áttekintés és célkitűzés
A **TabbedClient** egy erőforrás-hatékony, adatvédelmi fókuszú, cross-platform asztali és mobil alkalmazás (Rambox alternatíva), amely egyetlen ablakban, vertikálisan elrendezett fülek segítségével biztosít hozzáférést különféle webes szolgáltatásokhoz.

### Fő alapelvek
- **Zero-Telemetry (Zéró külső adatküldés):** Az alkalmazás semmilyen telemetriát, analitikát, hibaüzenet-küldést vagy háttérhívást nem végez harmadik fél szerverei felé. Az egyetlen hálózati forgalom a felhasználó által felvett weboldalak és azok közvetlen szerverei között zajlik.
- **Tiszta helyi állapotkezelés:** Minden konfiguráció, beállítás és munkamenet-adat a felhasználó saját gépén/eszközén tárolódik.
- **Konzolmentes fókusz:** A modern webalkalmazások (pl. Gmail, WhatsApp Web, Slack) JavaScript, WebSockets és Canvas függőségei miatt a szöveges terminálos (TUI) támogatás elhagyásra került. A célplatformok: **Linux GUI**, **Windows GUI** és **Android**.

---

## 2. Platformok és technológiai stack

| Réteg | Technológia | Indoklás |
| :--- | :--- | :--- |
| **Alkalmazáskeret** | **Tauri v2** | Natív webview integráció, minimális memóriahasználat, nulla telemetria, hivatalos Android és Desktop támogatás. |
| **Backend / Natív mag** | **Rust** | Biztonságos memóriakezelés, alacsony szintű webview pozicionálás, tray és partíció-kezelés. |
| **Frontend / UI** | **TypeScript + HTML5 + CSS3** | Könnyűsúlyú, keretrendszer-független vagy Svelte/Vanilla architektúra, reszponzív vertikális fülelrendezés. |
| **Webview (Linux)** | **WebKitGTK** (4.1+) | Linux asztali szabvány, különálló `WebKitWebsiteDataManager` adatmappákkal a fül-izolációhoz. |
| **Webview (Windows)** | **WebView2** (Chromium) | Windows natív beágyazott böngészőmotor különálló `UserDataFolder` partíciókkal. |
| **Webview (Android)** | **Android System WebView** | Natív beágyazott Android böngészőfelület. |

---

## 3. Funkcionális követelmények

### 3.1. Fülek és Munkamenet-izoláció (Multi-Account)
- Minden fülhöz hozzárendelhető egy **Profil / Partíció** azonosító (pl. `default`, `munka`, `magan`).
- Az azonos profilhoz tartozó fülek megosztják a bejelentkezéseket, a különböző profilokhoz tartozók azonban teljesen független böngészési adattárolóval (cookie jar, localStorage, session) futnak, lehetővé téve a párhuzamos fiókhasználatot egyazon szolgáltatáson belül.

### 3.2. Fülkezelő felület és Sablonok
- **Vertikális sáv:** Az ablak bal oldalán elhelyezkedő fülsáv ikonokkal, nevekkel és állapotjelzőkkel.
- **Összecsukható sáv (Compact / Icon-only nézet):** Az asztali felületen a bal oldali sáv egyetlen kattintással összecsukható egy vékony, helytakarékos sávvá, amelyen kizárólag a kerekített ikonok és az olvasatlan jelvények (badge) láthatóak. A kiválasztott szélességi állapot automatikusan elmentődik.
- **Téma támogatás:** Beépített témaválasztó az alábbi 5 jóváhagyott stílussal (induláskor az utoljára kiválasztott téma töltődik be):
  1. `slate`: Slate Studio (Minimalist Modern Dark)
  2. `nordic`: Nordic Crisp (Scandinavian Clean Light)
  3. `jetbrains`: JetBrains Obsidian (Functional Engineering Dark)
  4. `solarized`: Solarized Paper (Sepia / Academic Light)
  5. `enterprise`: Enterprise Cobalt (Corporate Clean Light)
- **Új fül hozzáadása modal:**
  - **Gyorsgombok (Presets):** WhatsApp Web, Telegram Web, Gmail, Discord, Slack, Trello, Google Calendar, ProtonMail, Notion.
  - **Egyedi URL mező:** Bármilyen érvényes `https://` webcím megadható.
  - **Fül neve és ikonja:** Automatikusan kitöltve a sablonból, vagy szabadon szerkeszthető.
  - **Profilválasztó:** Meglévő profil kiválasztása vagy új profilnév beírása.
- **Fülek rendezése és törlése:** Fülek sorrendjének módosítása és fül eltávolítása megerősítéssel.

### 3.3. Rendszerértesítések és Jelvények (Badge)
- A háttérben lévő fülek által kibocsátott HTML5 `Notification` eseményeket a kliens natív rendszerértesítésként továbbítja az operációs rendszer felé.
- A vertikális füleken számláló vagy pont (badge) jelzi az olvasatlan üzeneteket és új értesítéseket.

### 3.4. Rendszertálca (System Tray) és Háttérműködés (Desktop)
- Az ablak bezáró gombjára (`X`) kattintva az alkalmazás nem áll le, hanem a rendszertálcára minimalizálódik.
- A tálcaikon menüjéből elérhető:
  - Ablak megjelenítése / elrejtése
  - Fülek gyorsválasztása
  - Végleges kilépés (`Quit`)

### 3.5. Reszponzív felület (Desktop vs. Mobil)
- **Desktop (Linux, Windows):** Rögzített bal oldali sáv, kompakt (csak ikon) vagy bővített nézetben.
- **Mobil (Android):** Összecsukható oldalmenü (Navigation Drawer). A menü gombnyomással vagy ujjhúzással nyitható meg, biztosítva, hogy a weboldal megkapja a teljes kijelzőszélességet.

---

## 4. Adatmodell és Konfiguráció

A beállítások a felhasználó helyi konfigurációs könyvtárában tárolódnak `config.json` formátumban:

```json
{
  "version": "1.0.0",
  "settings": {
    "minimizeToTrayOnClose": true,
    "startMinimized": false,
    "theme": "dark",
    "sidebarCollapsed": false
  },
  "profiles": [
    { "id": "default", "name": "Alapértelmezett" },
    { "id": "work", "name": "Munkahelyi" },
    { "id": "personal", "name": "Magán" }
  ],
  "tabs": [
    {
      "id": "tab-1",
      "name": "WhatsApp",
      "url": "https://web.whatsapp.com",
      "icon": "whatsapp",
      "profileId": "personal",
      "notificationsEnabled": true,
      "order": 0
    },
    {
      "id": "tab-2",
      "name": "Slack",
      "url": "https://app.slack.com",
      "icon": "slack",
      "profileId": "work",
      "notificationsEnabled": true,
      "order": 1
    }
  ]
}
```

---

## 5. Telemetria- és Adatvédelmi nyilatkozat
1. **Nincs külső analytics szerver:** Nem tartalmaz Google Analytics, Sentry, Mixpanel, PostHog vagy bármilyen más adatgyűjtő könyvtárat.
2. **Közvetlen hálózati forgalom:** A webnézetek közvetlenül az adott domainekkel kommunikálnak (TLS titkosítással).
3. **Nincs felhőszinkronizáció:** Nincs külső központi fiók; a konfiguráció kizárólag helyi fájlrendszeren perzisztál.
