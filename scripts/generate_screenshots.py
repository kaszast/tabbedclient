#!/usr/bin/env python3
"""
TabbedClient — Képernyőkép-generáló automatizmus (Broadway GTK3 + WebKit2)
A valódi TabbedClientWindow ablakból készít pixelpontos, élethű és anonymizált képernyőképeket.
"""

import os
import subprocess
import time
import json
import gi

gi.require_version('Gtk', '3.0')
gi.require_version('WebKit2', '4.1')

PORT = ":32"
p = subprocess.Popen(['broadwayd', PORT], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(0.7)

os.environ['GDK_BACKEND'] = 'broadway'
os.environ['BROADWAY_DISPLAY'] = PORT

import sys
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, "desktop"))

from tabbedclient import TabbedClientWindow, Gtk, Gdk, GLib

SCREENSHOTS_DIR = os.path.join(BASE_DIR, "docs", "screenshots")
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

Gtk.init_check()

gmail_uri = GLib.filename_to_uri(os.path.join(BASE_DIR, "src", "mock_services", "gmail.html"), None)
slack_uri = GLib.filename_to_uri(os.path.join(BASE_DIR, "src", "mock_services", "slack.html"), None)
cal_uri = GLib.filename_to_uri(os.path.join(BASE_DIR, "src", "mock_services", "calendar.html"), None)

SAMPLE_TABS = [
    {
        "id": "tab-gmail",
        "title": "Gmail",
        "name": "Gmail",
        "url": gmail_uri,
        "icon": "gmail",
        "profile": "personal",
        "profileId": "personal",
        "notificationsEnabled": True,
        "unreadCount": 12,
        "order": 0
    },
    {
        "id": "tab-slack",
        "title": "Slack",
        "name": "Slack",
        "url": slack_uri,
        "icon": "slack",
        "profile": "work",
        "profileId": "work",
        "notificationsEnabled": True,
        "unreadCount": 4,
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
        "unreadCount": 2,
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
        "unreadCount": 0,
        "order": 3
    },
    {
        "id": "tab-calendar",
        "title": "Google Naptár",
        "name": "Google Naptár",
        "url": cal_uri,
        "icon": "calendar",
        "profile": "work",
        "profileId": "work",
        "notificationsEnabled": True,
        "unreadCount": 0,
        "order": 4
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
        "order": 5
    }
]


def snap_window(win, filename):
    while Gtk.events_pending():
        Gtk.main_iteration_do(False)
    
    gdk_win = win.get_window()
    if gdk_win:
        w, h = win.get_size()
        pixbuf = Gdk.pixbuf_get_from_window(gdk_win, 0, 0, w, h)
        if pixbuf:
            out_path = os.path.join(SCREENSHOTS_DIR, filename)
            pixbuf.savev(out_path, "png", [], [])
            print(f"   ✓ Mentve: {filename} ({w}x{h}, {os.path.getsize(out_path):,} bájt)")
            return True
    print(f"   ✗ Hiba: nem sikerült a mentés ({filename})")
    return False


def set_collapsed(win, collapsed: bool):
    win.config["sidebarCollapsed"] = collapsed
    win.config.setdefault("settings", {})["sidebarCollapsed"] = collapsed
    win._apply_sidebar_width(collapsed)
    win.sync_all_views()


def set_theme(win, theme_name: str):
    win.config["theme"] = theme_name
    win.config.setdefault("settings", {})["theme"] = theme_name
    win.sync_all_views()


def run_pipeline():
    print("TabbedClient UI Példányosítása...")
    win = TabbedClientWindow()
    win.set_default_size(1280, 800)
    win.config["tabs"] = SAMPLE_TABS
    set_collapsed(win, False)
    set_theme(win, "slate")

    for t in SAMPLE_TABS:
        win._ensure_tab_webview(t)

    win.show_all()
    win.sync_all_views()

    loop = GLib.MainLoop()

    steps = [
        # (Lépésnév, Action_lambda, Képfájlnév, Várakozás_ms)
        (
            "1. Hero Main: Nyitott fülsáv + Élethű Anonymizált Gmail",
            lambda: (
                set_collapsed(win, False),
                set_theme(win, "slate"),
                win.switch_to_tab("tab-gmail"),
                win.sync_all_views()
            ),
            "hero_main.png",
            2500
        ),
        (
            "2. Dashboard Overview: Fülsáv + Bento Irányítópult",
            lambda: (
                win.switch_to_tab("home"),
                win.welcome_webview.run_javascript("if (window.showView) window.showView('dashboard');", None, None, None),
                win.sync_all_views()
            ),
            "dashboard_overview.png",
            1500
        ),
        (
            "3. Theme Slate Studio: Teljes felület",
            lambda: (
                set_theme(win, "slate"),
                win.sync_all_views()
            ),
            "theme_slate.png",
            1200
        ),
        (
            "4. Theme Nordic Crisp: Teljes felület",
            lambda: (
                set_theme(win, "nordic"),
                win.sync_all_views()
            ),
            "theme_nordic.png",
            1200
        ),
        (
            "5. Theme JetBrains Obsidian: Teljes felület",
            lambda: (
                set_theme(win, "jetbrains"),
                win.sync_all_views()
            ),
            "theme_jetbrains.png",
            1200
        ),
        (
            "6. Theme Solarized Paper: Teljes felület",
            lambda: (
                set_theme(win, "solarized"),
                win.sync_all_views()
            ),
            "theme_solarized.png",
            1200
        ),
        (
            "7. Theme Enterprise Cobalt: Teljes felület",
            lambda: (
                set_theme(win, "enterprise"),
                win.sync_all_views()
            ),
            "theme_enterprise.png",
            1200
        ),
        (
            "8. Kompakt Fülsáv (Icon-only 48px mód) + Gmail",
            lambda: (
                set_theme(win, "slate"),
                win.switch_to_tab("tab-gmail"),
                set_collapsed(win, True)
            ),
            "feature_compact_sidebar.png",
            1500
        ),
        (
            "9. Partíciók és Munkahelyi Slack",
            lambda: (
                set_collapsed(win, False),
                win.switch_to_tab("tab-slack"),
                win.sync_all_views()
            ),
            "feature_partitions.png",
            1500
        ),
        (
            "10. Új Fül Hozzáadása & Sablonok",
            lambda: (
                win.switch_to_tab("home"),
                win.welcome_webview.run_javascript("if (window.showView) window.showView('add-tab');", None, None, None),
                win.sync_all_views()
            ),
            "feature_presets_modal.png",
            1200
        ),
        (
            "11. Beállítások és Témaválasztó Lap",
            lambda: (
                win.welcome_webview.run_javascript("if (window.showView) window.showView('settings');", None, None, None),
                win.sync_all_views()
            ),
            "dashboard_themes_view.png",
            1200
        ),
    ]

    step_idx = 0

    def execute_next_step():
        nonlocal step_idx
        if step_idx < len(steps):
            name, action, fname, wait_ms = steps[step_idx]
            print(f"-> Végrehajtás: {name}...")
            action()
            step_idx += 1
            GLib.timeout_add(wait_ms, capture_current_step, fname)
        else:
            print("\n[SIKER] Minden valódi TabbedClient képernyőkép sikeresen legenerálva!")
            loop.quit()

    def capture_current_step(fname):
        snap_window(win, fname)
        GLib.timeout_add(300, execute_next_step)

    # Indítás előtti inicializációs várakozás: 3.5 mp a WebKit stabilizálódására
    GLib.timeout_add(3500, execute_next_step)
    loop.run()

    win.destroy()


def main():
    try:
        run_pipeline()
    finally:
        p.kill()


if __name__ == "__main__":
    main()
