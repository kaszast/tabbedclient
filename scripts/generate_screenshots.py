#!/usr/bin/env python3
"""
TabbedClient — Professzionális Képernyőkép-generáló automatizmus (Broadway GTK3 + WebKit2)
Előállítja a README.md-hez szükséges illusztrációkat és képernyőképeket.
"""

import os
import subprocess
import time
import json
import gi

gi.require_version('Gtk', '3.0')
gi.require_version('WebKit2', '4.1')

PORT = ":15"
p = subprocess.Popen(['broadwayd', PORT], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(0.6)

os.environ['GDK_BACKEND'] = 'broadway'
os.environ['BROADWAY_DISPLAY'] = PORT

from gi.repository import Gtk, WebKit2, GLib

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCREENSHOTS_DIR = os.path.join(BASE_DIR, "docs", "screenshots")
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

Gtk.init_check()

SAMPLE_TABS = [
    {
        "id": "tab-gmail",
        "title": "Gmail (Magán)",
        "name": "Gmail (Magán)",
        "url": "https://mail.google.com",
        "icon": "gmail",
        "profile": "personal",
        "profileId": "personal",
        "notificationsEnabled": True,
        "unreadCount": 5,
        "order": 0
    },
    {
        "id": "tab-slack",
        "title": "Slack (Munkacsoport)",
        "name": "Slack (Munkacsoport)",
        "url": "https://slack.com",
        "icon": "slack",
        "profile": "work",
        "profileId": "work",
        "notificationsEnabled": True,
        "unreadCount": 12,
        "order": 1
    },
    {
        "id": "tab-whatsapp",
        "title": "WhatsApp Web",
        "name": "WhatsApp Web",
        "url": "https://web.whatsapp.com",
        "icon": "whatsapp",
        "profile": "personal",
        "profileId": "personal",
        "notificationsEnabled": True,
        "unreadCount": 0,
        "order": 2
    },
    {
        "id": "tab-telegram",
        "title": "Telegram",
        "name": "Telegram",
        "url": "https://web.telegram.org",
        "icon": "telegram",
        "profile": "personal",
        "profileId": "personal",
        "notificationsEnabled": True,
        "unreadCount": 3,
        "order": 3
    },
    {
        "id": "tab-notion",
        "title": "Notion Docs",
        "name": "Notion Docs",
        "url": "https://notion.so",
        "icon": "notion",
        "profile": "work",
        "profileId": "work",
        "notificationsEnabled": True,
        "unreadCount": 0,
        "order": 4
    }
]


def capture_view(filename, target_url, script_to_eval=None, width=1280, height=800, delay_ms=500):
    print(f"-> Generálás: {filename} ({width}x{height})...")
    win = Gtk.OffscreenWindow()
    win.set_default_size(width, height)

    wv = WebKit2.WebView()
    w_settings = wv.get_settings()
    w_settings.set_enable_javascript(True)
    w_settings.set_allow_file_access_from_file_urls(True)
    w_settings.set_allow_universal_access_from_file_urls(True)
    if hasattr(w_settings, "set_zoom_text_only"):
        w_settings.set_zoom_text_only(False)

    win.add(wv)
    win.show_all()

    wv.load_uri(target_url)

    loop = GLib.MainLoop()

    def on_load_changed(view, event):
        if event == WebKit2.LoadEvent.FINISHED:
            if script_to_eval:
                view.run_javascript(script_to_eval, None, on_script_finished, None)
            else:
                GLib.timeout_add(delay_ms, take_snapshot)

    def on_script_finished(view, result, user_data):
        GLib.timeout_add(delay_ms, take_snapshot)

    def take_snapshot():
        pixbuf = win.get_pixbuf()
        if pixbuf:
            out_path = os.path.join(SCREENSHOTS_DIR, filename)
            pixbuf.savev(out_path, "png", [], [])
            print(f"   ✓ Mentve: {out_path} ({os.path.getsize(out_path):,} bájt)")
        else:
            print(f"   ✗ Hiba: Pixbuf üres volt a {filename} fájlhoz.")
        loop.quit()

    wv.connect("load-changed", on_load_changed)
    GLib.timeout_add(6000, loop.quit)
    loop.run()
    win.destroy()


def main():
    try:
        index_url = GLib.filename_to_uri(os.path.join(BASE_DIR, "src", "index.html"), None)
        welcome_url = GLib.filename_to_uri(os.path.join(BASE_DIR, "src", "welcome.html"), None)
        tabs_json = json.dumps(SAMPLE_TABS)

        # 1. Hero Main: Nyitott oldalsáv, aktív fülek, profiljelzők, unread jelvények
        capture_view("hero_main.png", index_url, script_to_eval=f"""
        if (window.tabbedApp) {{
            window.tabbedApp.config.tabs = {tabs_json};
            window.tabbedApp.config.activeTabId = 'tab-gmail';
            window.tabbedApp.setTheme('slate', false);
            window.tabbedApp.renderTabs();
            window.tabbedApp.selectTab('tab-gmail');
        }}
        """, width=1280, height=820)

        # 2. Welcome Dashboard (Irányítópult Bento logóval, statisztikákkal, gyorsgombokkal)
        capture_view("dashboard_overview.png", welcome_url, script_to_eval=f"""
        if (window.syncFromBackend) {{
            window.syncFromBackend({{
                theme: 'slate',
                tabs: {tabs_json},
                activeTabId: 'tab-gmail',
                view: 'dashboard',
                settings: {{ theme: 'slate', minimizeToTrayOnClose: true }}
            }});
        }}
        """, width=1200, height=800)

        # 3. Az 5 Jóváhagyott Téma képernyőképei teljes felülettel és fülekkel
        themes = [
            ("theme_slate.png", "slate", "01. Slate Studio"),
            ("theme_nordic.png", "nordic", "02. Nordic Crisp"),
            ("theme_jetbrains.png", "jetbrains", "03. JetBrains Obsidian"),
            ("theme_solarized.png", "solarized", "08. Solarized Paper"),
            ("theme_enterprise.png", "enterprise", "10. Enterprise Cobalt")
        ]

        for fname, th_id, th_name in themes:
            capture_view(fname, index_url, script_to_eval=f"""
            if (window.tabbedApp) {{
                window.tabbedApp.config.tabs = {tabs_json};
                window.tabbedApp.config.activeTabId = 'tab-gmail';
                window.tabbedApp.setTheme('{th_id}', false);
                window.tabbedApp.renderTabs();
                window.tabbedApp.selectTab('tab-gmail');
            }}
            """, width=1200, height=760)

        # 4. Új Fül Modál (9 beépített szolgáltatás-sablon, egyedi URL és profilválasztó)
        capture_view("feature_presets_modal.png", index_url, script_to_eval=f"""
        if (window.tabbedApp) {{
            window.tabbedApp.config.tabs = {tabs_json};
            window.tabbedApp.renderTabs();
            const modal = document.getElementById('add-tab-modal');
            if (modal) modal.classList.add('active');
        }}
        """, width=1200, height=760)

        # 5. Beállítások Modál (5 téma interaktív választóval, tálca viselkedéssel)
        capture_view("feature_settings_modal.png", index_url, script_to_eval=f"""
        if (window.tabbedApp) {{
            window.tabbedApp.config.tabs = {tabs_json};
            window.tabbedApp.renderTabs();
            const modal = document.getElementById('settings-modal');
            if (modal) modal.classList.add('active');
        }}
        """, width=1200, height=760)

        # 6. Kompakt Vertikális Fülsáv (Icon-only mód 2x-es ikonmérettel és számlálókkal)
        capture_view("feature_compact_sidebar.png", index_url, script_to_eval=f"""
        if (window.tabbedApp) {{
            window.tabbedApp.config.tabs = {tabs_json};
            window.tabbedApp.setTheme('jetbrains', false);
            window.tabbedApp.setSidebarCollapsed(true, false);
            window.tabbedApp.renderTabs();
        }}
        """, width=1200, height=760)

        # 7. Irányítópult Beállítások és Témaválasztó előnézeti lap
        capture_view("dashboard_themes_view.png", welcome_url, script_to_eval=f"""
        if (window.syncFromBackend) {{
            window.syncFromBackend({{
                theme: 'slate',
                tabs: {tabs_json},
                view: 'settings'
            }});
        }}
        """, width=1200, height=800)

        # 8. Munkamenet-Izoláció és Profilkezelés a fülsávban
        capture_view("feature_partitions.png", index_url, script_to_eval=f"""
        if (window.tabbedApp) {{
            window.tabbedApp.config.tabs = {tabs_json};
            window.tabbedApp.setTheme('slate', false);
            window.tabbedApp.renderTabs();
            window.tabbedApp.selectTab('tab-slack');
        }}
        """, width=1200, height=760)

        print("\n[SIKER] Minden képernyőkép frissítve a docs/screenshots/ mappában.")

    finally:
        p.kill()


if __name__ == "__main__":
    main()
