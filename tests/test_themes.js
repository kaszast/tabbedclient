/**
 * TabbedClient - Témarendszer és Stíluslap Validációs Teszt
 */

const assert = require('assert');
const fs = require('fs');
const path = require('path');
const { THEMES } = require('../src/config.js');

function runThemesTests() {
  console.log('--- [Teszt] Témarendszer és Stílusok Ellenőrzése ---');

  // 1. Az 5 jóváhagyott téma megléte
  const expectedThemes = ['slate', 'nordic', 'jetbrains', 'solarized', 'enterprise'];
  expectedThemes.forEach(themeId => {
    assert.ok(THEMES[themeId], `A jóváhagyott témának szerepelnie kell: ${themeId}`);
    assert.ok(THEMES[themeId].name, `A témának kell név: ${themeId}`);
    assert.ok(THEMES[themeId].type, `A témának kell típus (dark/light): ${themeId}`);
  });

  // 2. CSS stíluslap ellenőrzése
  const cssPath = path.join(__dirname, '../src/styles.css');
  assert.ok(fs.existsSync(cssPath), 'A styles.css fájlnak léteznie kell');
  const cssContent = fs.readFileSync(cssPath, 'utf-8');

  // Minden témához tartoznia kell CSS osztálynak
  expectedThemes.forEach(themeId => {
    assert.ok(
      cssContent.includes(`.theme-${themeId}`),
      `A CSS-nek tartalmaznia kell a(z) .theme-${themeId} szelektor definícióját`
    );
  });

  // Összecsukható sáv osztályainak és kompakt (48px ikon-méretű) szélességének megléte
  assert.ok(cssContent.includes('.sidebar.collapsed'), 'A CSS-nek tartalmaznia kell az összecsukott oldalsáv stílust');
  assert.ok(cssContent.includes('width: 48px'), 'Az összecsukott oldalsávnak 48px kompakt ikonszélességűnek kell lennie');
  assert.ok(cssContent.includes('mobile-open'), 'A CSS-nek tartalmaznia kell a mobil drawer stílust');
  assert.ok(cssContent.includes('width: 32px') && cssContent.includes('height: 32px'), 'A fül-ikonoknak 32px (2x nagyobb) méretűnek kell lenniük');

  // Desktop futtató: 48px összecsukott méret és törlési megerősítő dialógus ellenőrzése
  const pyPath = path.join(__dirname, '../desktop/tabbedclient.py');
  const pyContent = fs.readFileSync(pyPath, 'utf-8');
  assert.ok(pyContent.includes('SIDEBAR_COLLAPSED_WIDTH = 48'), 'A desktop kliensnek 48px összecsukott sidebar szélességet kell alkalmaznia');
  assert.ok(pyContent.includes('Gtk.MessageDialog') && pyContent.includes('Biztosan törölni szeretnéd'), 'A szolgáltatás törlése előtt megerősítő dialógust kell megjeleníteni');

  // Alkalmazás ikon integritás ellenőrzése (Bento dizájn család)
  const iconsDir = path.join(__dirname, '../src-tauri/icons');
  ['icon.png', 'icon.svg', 'icon.ico', '128x128.png', '32x32.png'].forEach(file => {
    assert.ok(fs.existsSync(path.join(iconsDir, file)), `Az alkalmazás ikonnak léteznie kell: ${file}`);
  });

  console.log('✓ Az 5 téma, a kompakt oldalsáv és a törlési megerősítés validációja sikeres.');
}

runThemesTests();
