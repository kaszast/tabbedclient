#!/usr/bin/env python3
"""
Egységtesztek az olvasatlan számláló (unread badge) kinyerésének pontosságára,
az ismert szolgáltatások ikonfelismerésére (resolve_service_icon)
és a verziószám projekt-szintű egységességére (1.2).
"""

import json
import os
import re
import unittest

from desktop.tabbedclient import extract_unread_count, resolve_service_icon, DEFAULT_CONFIG
from scripts.build_packages import get_project_version


class TestVersionConsistency(unittest.TestCase):
    """Ellenőrzi, hogy a projekt összes komponense egységesen a pontos '1.2' verziót használja."""

    def test_version_unification(self):
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # 1. package.json
        pkg_path = os.path.join(project_root, "package.json")
        with open(pkg_path, "r", encoding="utf-8") as f:
            pkg = json.load(f)
        self.assertEqual(pkg.get("version"), "1.2")

        # 2. build_packages.py
        self.assertEqual(get_project_version(), "1.2")

        # 3. desktop/tabbedclient.py DEFAULT_CONFIG
        self.assertEqual(DEFAULT_CONFIG.get("version"), "1.2")

        # 4. data/config.json.template
        tpl_path = os.path.join(project_root, "data", "config.json.template")
        with open(tpl_path, "r", encoding="utf-8") as f:
            tpl = json.load(f)
        self.assertEqual(tpl.get("version"), "1.2")

        # 5. src-tauri/tauri.conf.json
        tauri_path = os.path.join(project_root, "src-tauri", "tauri.conf.json")
        with open(tauri_path, "r", encoding="utf-8") as f:
            tauri_cfg = json.load(f)
        self.assertEqual(tauri_cfg.get("version"), "1.2")

        # 6. src/welcome.html badge szöveg
        welcome_path = os.path.join(project_root, "src", "welcome.html")
        with open(welcome_path, "r", encoding="utf-8") as f:
            welcome_content = f.read()
        self.assertIn('>v1.2</span>', welcome_content)


class TestServiceIconResolution(unittest.TestCase):
    """Ellenőrzi, hogy az ismert szolgáltatások a beépített vektoros ikont kapják dinamikus favicon helyett."""

    def test_service_icon_detection(self):
        self.assertEqual(resolve_service_icon("Gmail (Magán)", "https://mail.google.com"), "gmail")
        self.assertEqual(resolve_service_icon("Google Naptár", "https://calendar.google.com"), "calendar")
        self.assertEqual(resolve_service_icon("Google Calendar", "https://calendar.google.com"), "calendar")
        self.assertEqual(resolve_service_icon("FB Messenger", "https://www.messenger.com/"), "messenger")
        self.assertEqual(resolve_service_icon("WhatsApp Web", "https://web.whatsapp.com"), "whatsapp")
        self.assertEqual(resolve_service_icon("Telegram", "https://web.telegram.org"), "telegram")
        self.assertEqual(resolve_service_icon("Slack", "https://app.slack.com"), "slack")
        self.assertEqual(resolve_service_icon("Microsoft Teams", "https://teams.microsoft.com"), "teams")
        self.assertEqual(resolve_service_icon("Discord", "https://discord.com/app"), "discord")
        self.assertEqual(resolve_service_icon("Notion", "https://notion.so"), "notion")
        self.assertEqual(resolve_service_icon("Trello", "https://trello.com"), "trello")
        self.assertEqual(resolve_service_icon("ProtonMail", "https://mail.proton.me"), "mail")

        # Ismeretlen egyéni weboldal globe marad
        self.assertEqual(resolve_service_icon("Céges Intranet", "https://intranet.example.com"), "globe")
        self.assertEqual(resolve_service_icon("Hírek", "https://index.hu"), "globe")


class TestUnreadCountExtraction(unittest.TestCase):
    """Ellenőrzi a valós olvasatlan számláló kinyerését és a hamis pozitívok kizárását."""

    def test_valid_unread_patterns(self):
        # Cím legelején lévő zárójeles számok
        self.assertEqual(extract_unread_count("(3) Gmail - maci@gmail.com", "https://mail.google.com"), 3)
        self.assertEqual(extract_unread_count("*(1) Google Chat", "https://chat.google.com"), 1)
        self.assertEqual(extract_unread_count("[5] Slack | dev-channel", "https://slack.com"), 5)
        self.assertEqual(extract_unread_count("(99+) WhatsApp", "https://web.whatsapp.com"), 99)
        self.assertEqual(extract_unread_count("(12) Messenger", "https://www.messenger.com"), 12)

        # Mappa/szolgáltatás neve utáni zárójeles számok
        self.assertEqual(extract_unread_count("Gmail — Beérkező levelek (12)", "https://mail.google.com"), 12)
        self.assertEqual(extract_unread_count("Inbox (7) - Work Mail", "https://mail.work.com"), 7)
        self.assertEqual(extract_unread_count("Beérkező levelek (4) - Gmail", "https://mail.google.com"), 4)
        self.assertEqual(extract_unread_count("Beérkezett üzenetek (2) - Outlook", "https://outlook.live.com"), 2)

        # Cím legvégén lévő csevegő számlálók
        self.assertEqual(extract_unread_count("Telegram (5)", "https://web.telegram.org"), 5)
        self.assertEqual(extract_unread_count("Telegram Web (3)", "https://web.telegram.org"), 3)
        self.assertEqual(extract_unread_count("Slack (2)", "https://slack.com"), 2)
        self.assertEqual(extract_unread_count("Discord (8)", "https://discord.com"), 8)

    def test_no_false_positives(self):
        # Üres vagy szám nélküli címek
        self.assertEqual(extract_unread_count("", "https://example.com"), 0)
        self.assertEqual(extract_unread_count("WhatsApp", "https://web.whatsapp.com"), 0)
        self.assertEqual(extract_unread_count("Telegram", "https://web.telegram.org"), 0)
        self.assertEqual(extract_unread_count("Beérkező levelek - felhasznalo@gmail.com - Gmail", "https://mail.google.com"), 0)
        self.assertEqual(extract_unread_count("Slack | General", "https://slack.com"), 0)

        # Google Naptár címében lévő dátumok sosem minősülhetnek olvasatlan levélnek
        self.assertEqual(extract_unread_count("Google Naptár - 2026. október 30., péntek", "https://calendar.google.com"), 0)
        self.assertEqual(extract_unread_count("Google Calendar - October 30", "https://calendar.google.com"), 0)
        self.assertEqual(extract_unread_count("Google Naptár (30)", "https://calendar.google.com"), 0)

        # Levél tárgyában lévő dátumok, verziók és sorszámok nem téveszthetik meg a számlálót
        self.assertEqual(extract_unread_count("Megbeszélés jegyzőkönyv (2026.10.28)", "https://mail.google.com"), 0)
        self.assertEqual(extract_unread_count("Éves pénzügyi beszámoló (2025)", "https://mail.google.com"), 0)
        self.assertEqual(extract_unread_count("Hírlevél (1. rész) - Technológiai hírek", "https://mail.google.com"), 0)
        self.assertEqual(extract_unread_count("Fontos teendők (12 pontban)", "https://mail.google.com"), 0)
        self.assertEqual(extract_unread_count("Projekt dokumentáció (v1.2)", "https://mail.google.com"), 0)

    def test_template_initial_unread_zero(self):
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        tpl_path = os.path.join(project_root, "data", "config.json.template")
        with open(tpl_path, "r", encoding="utf-8") as f:
            tpl = json.load(f)
        for tab in tpl.get("tabs", []):
            self.assertEqual(tab.get("unreadCount", 0), 0, f"A(z) {tab.get('id')} fül alapértelmezett számlálója nem 0")


if __name__ == "__main__":
    unittest.main()
