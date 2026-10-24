/**
 * TabbedClient - Fül- és Konfiguráció Egységtesztek
 */

const assert = require('assert');
const { DEFAULT_CONFIG, PRESETS, THEMES } = require('../src/config.js');

function runTabsTests() {
  console.log('--- [Teszt] Konfiguráció és Fülkezelés Ellenőrzése ---');

  // 1. Alapértelmezett konfiguráció integritása
  assert.ok(DEFAULT_CONFIG.version, 'A konfigurációnak rendelkeznie kell verziószámmal');
  assert.strictEqual(DEFAULT_CONFIG.settings.minimizeToTrayOnClose, true, 'Az alapértelmezett tray viselkedés true kell legyen');
  assert.ok(Array.isArray(DEFAULT_CONFIG.tabs), 'A tabs mező tömb kell legyen');

  // 2. Munkamenet-izoláció (Multi-account partíciók)
  const profiles = DEFAULT_CONFIG.profiles.map(p => p.id);
  assert.ok(profiles.includes('work'), 'A munkahelyi profilnak léteznie kell');
  assert.ok(profiles.includes('personal'), 'A magán profilnak léteznie kell');

  DEFAULT_CONFIG.tabs.forEach(tab => {
    assert.ok(tab.id, `A fülnek kötelező az ID: ${JSON.stringify(tab)}`);
    assert.ok(tab.url.startsWith('https://'), `A fül URL-jének https-nek kell lennie: ${tab.url}`);
    assert.ok(tab.profileId, `A fülhöz partíció/profil azonosító szükséges: ${tab.name}`);
  });

  // 3. Beépített sablonok ellenőrzése (spec.md 3.2 alapján mind a 9 specifikált sablon)
  const requiredPresets = ['whatsapp', 'slack', 'telegram', 'gmail', 'discord', 'trello', 'calendar', 'notion', 'protonmail'];
  const presentPresets = PRESETS.map(p => p.id);
  requiredPresets.forEach(presetId => {
    assert.ok(presentPresets.includes(presetId), `A specifikált sablonnak szerepelnie kell: ${presetId}`);
  });

  // 4. sidebar.html és welcome.html beágyazott szkriptek szintaxis- és szinkronizáció-tesztje
  const fs = require('fs');
  const path = require('path');
  const vm = require('vm');

  const dummyEl = () => {
    const el = {
      addEventListener: () => {},
      appendChild: () => {},
      querySelector: () => dummyEl(),
      querySelectorAll: () => [],
      classList: { add: () => {}, remove: () => {}, toggle: () => {} },
      style: {},
      dataset: {},
      innerHTML: '',
      textContent: '',
      value: '',
      focus: () => {}
    };
    return el;
  };

  ['sidebar.html', 'welcome.html'].forEach(fileName => {
    const html = fs.readFileSync(path.join(__dirname, '../src', fileName), 'utf8');
    const scripts = [...html.matchAll(/<script(?:\s+src="([^"]+)")?>([\s\S]*?)<\/script>/g)];
    const win = { addEventListener: () => {}, webkit: { messageHandlers: { tabbedclient: { postMessage: () => {} } } } };
    const doc = {
      body: dummyEl(),
      getElementById: () => dummyEl(),
      querySelectorAll: () => [],
      createElement: () => dummyEl(),
      addEventListener: () => {}
    };
    const ctx = vm.createContext({ window: win, document: doc, console, setTimeout });
    scripts.forEach(match => {
      if (match[1]) {
        const extCode = fs.readFileSync(path.join(__dirname, '../src', match[1]), 'utf8');
        vm.runInContext(extCode, ctx);
      } else {
        vm.runInContext(match[2], ctx);
      }
    });
    assert.strictEqual(typeof win.syncFromBackend, 'function', `${fileName}: window.syncFromBackend függvénynek léteznie kell`);
    win.syncFromBackend({
      theme: 'jetbrains',
      sidebarCollapsed: false,
      activeTabId: 'tab-1',
      tabs: [{ id: 'tab-1', title: 'Teszt', url: 'https://www.index.hu', profile: 'personal' }],
      view: 'dashboard'
    });
  });

  // 5. Desktop (Python) futtató funkcionális ellenőrzése
  const pyCode = fs.readFileSync(path.join(__dirname, '../desktop/tabbedclient.py'), 'utf8');
  assert.ok(pyCode.includes('setup_tray'), 'A desktop futtatónak tartalmaznia kell a rendszertálca (tray) támogatást');
  assert.ok(pyCode.includes('_on_show_notification'), 'A desktop futtatónak tartalmaznia kell a HTML5 értesítés-kezelést');
  assert.ok(pyCode.includes('_on_permission_request'), 'A desktop futtatónak tartalmaznia kell a biztonságos jogosultságkezelést');
  assert.ok(pyCode.includes('move_tab'), 'A desktop futtatónak támogatnia kell a fülek átrendezését');
  assert.ok(pyCode.includes('toggle_tab_notifications'), 'A desktop futtatónak támogatnia kell az értesítések fülönkénti némítását');
  assert.ok(pyCode.includes('open_external_uri'), 'A desktop futtatónak tartalmaznia kell a külső linkek megnyitását');
  assert.ok(pyCode.includes('_on_decide_policy'), 'A desktop futtatónak kezelnie kell a decide-policy szignált');
  assert.ok(pyCode.includes('_on_create_webview'), 'A desktop futtatónak kezelnie kell a create (target=_blank) szignált');
  assert.ok(pyCode.includes('set_default_icon_list'), 'A desktop futtatónak be kell állítania a több-méretű ikonkészletet');
  assert.ok(fs.existsSync(path.join(__dirname, '../install_desktop_entry.sh')), 'Az install_desktop_entry.sh fájlnak léteznie kell');
  assert.ok(fs.existsSync(path.join(__dirname, '../scripts/install_desktop.py')), 'A scripts/install_desktop.py fájlnak léteznie kell');

  // 6. Külső hivatkozások felismerésének egységtesztje (Python modul)
  const { execSync } = require('child_process');
  execSync(`python3 -c "
import sys
sys.path.insert(0, 'desktop')
from tabbedclient import is_external_link, extract_real_target_url

# Gmail view in browser / külső link tesztek
assert is_external_link('https://mail.google.com', 'https://www.google.com/url?q=https%3A%2F%2Fgithub.com&sa=D') == True
assert is_external_link('https://mail.google.com', 'https://newsletter.example.org/view-in-browser') == True
assert is_external_link('https://mail.google.com', 'https://mail.google.com/mail/u/0/#inbox') == False
assert is_external_link('https://mail.google.com', 'https://accounts.google.com/signin') == False
assert is_external_link('https://app.slack.com', 'https://example.com/doc') == True
assert extract_real_target_url('https://www.google.com/url?q=https%3A%2F%2Fexample.com') == 'https://example.com'
"`, { stdio: 'inherit' });

  console.log('✓ Minden fül-, konfigurációs és WebView-szinkronizációs teszt sikeresen lefutott.');
}

runTabsTests();
