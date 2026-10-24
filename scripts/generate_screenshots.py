#!/usr/bin/env python3
"""
TabbedClient — Professzionális Képernyőkép-generáló automatizmus (Broadway GTK3 + WebKit2)
A valódi TabbedClientWindow ablakból készít pixelpontos, anonymizált képernyőképeket.
"""

import os
import subprocess
import time
import json
import gi

gi.require_version('Gtk', '3.0')
gi.require_version('WebKit2', '4.1')

PORT = ":30"
p = subprocess.Popen(['broadwayd', PORT], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(0.6)

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
        "unreadCount": 4,
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
        "unreadCount": 8,
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


def snap_window(win, filename, width=1280, height=800):
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


def run_pipeline():
    print("TabbedClient UI Példányosítása...")
    win = TabbedClientWindow()
    win.set_default_size(1280, 800)
    win.config["tabs"] = SAMPLE_TABS
    for t in SAMPLE_TABS:
        win._ensure_tab_webview(t)

    win.show_all()

    loop = GLib.MainLoop()

    steps = [
        # (Lépésnév, Action_lambda, Képfájlnév, Várakozás_ms)
        ("1. Hero Main: Nyitott fülsáv + Anonymizált Gmail", lambda: (win.switch_to_tab("tab-gmail"), win.sync_all_views()), "hero_main.png", 1500),
        ("2. Dashboard Overview: Fülsáv + Bento Irányítópult", lambda: (win.switch_to_tab("home"), win.sync_all_views()), "dashboard_overview.png", 1200),
        ("3. Theme Slate Studio: Teljes felület", lambda: (win.config.update({"theme": "slate"}), win.sync_all_views()), "theme_slate.png", 1000),
        ("4. Theme Nordic Crisp: Teljes felület", lambda: (win.config.update({"theme": "nordic"}), win.sync_all_views()), "theme_nordic.png", 1000),
        ("5. Theme JetBrains Obsidian: Teljes felület", lambda: (win.config.update({"theme": "jetbrains"}), win.sync_all_views()), "theme_jetbrains.png", 1000),
        ("6. Theme Solarized Paper: Teljes felület", lambda: (win.config.update({"theme": "solarized"}), win.sync_all_views()), "theme_solarized.png", 1000),
        ("7. Theme Enterprise Cobalt: Teljes felület", lambda: (win.config.update({"theme": "enterprise"}), win.sync_all_views()), "theme_enterprise.png", 1000),
        ("8. Kompakt Fülsáv (Icon-only 48px mód)", lambda: (win.config.update({"sidebarCollapsed": True, "theme": "slate"}), win._apply_sidebar_width(True), win.sync_all_views()), "feature_compact_sidebar.png", 1000),
        ("9. Partíciók és Munkahelyi Slack", lambda: (win.config.update({"sidebarCollapsed": False}), win._apply_sidebar_width(False), win.switch_to_tab("tab-slack"), win.sync_all_views()), "feature_partitions.png", 1200),
        ("10. Új Fül Hozzáadása & Sablonok", lambda: (win.switch_to_tab("home"), win.welcome_webview.run_javascript("if (window.showView) window.showView('add-tab');", None, None, None)), "feature_presets_modal.png", 1000),
        ("11. Beállítások és Témaválasztó Lap", lambda: (win.welcome_webview.run_javascript("if (window.showView) window.showView('settings');", None, None, None)), "dashboard_themes_view.png", 1000),
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
        GLib.timeout_add(200, execute_next_step)

    # Indítás
    GLib.timeout_add(1500, execute_next_step)
    loop.run()

    win.destroy()


def main():
    try:
        run_pipeline()
    finally:
        p.kill()


if __name__ == "__main__":
    main()
