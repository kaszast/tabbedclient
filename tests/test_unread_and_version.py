#!/usr/bin/env python3
"""
Egységtesztek az olvasatlan számláló (unread badge) kinyerésének pontosságára
és a verziószám projekt-szintű egységességére (1.1).
"""

import json
import os
import re
import unittest

from desktop.tabbedclient import extract_unread_count, DEFAULT_CONFIG
from scripts.build_packages import get_project_version


class TestVersionConsistency(unittest.TestCase):
    """Ellenőrzi, hogy a projekt összes komponense egységesen a pontos '1.1' verziót használja."""

    def test_version_unification(self):
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # 1. package.json
        pkg_path = os.path.join(project_root, "package.json")
        with open(pkg_path, "r", encoding="utf-8") as f:
            pkg = json.load(f)
        self.assertEqual(pkg.get("version"), "1.1")

        # 2. build_packages.py
        self.assertEqual(get_project_version(), "1.1")

        # 3. desktop/tabbedclient.py DEFAULT_CONFIG
        self.assertEqual(DEFAULT_CONFIG.get("version"), "1.1")

        # 4. data/config.json.template
        tpl_path = os.path.join(project_root, "data", "config.json.template")
        with open(tpl_path, "r", encoding="utf-8") as f:
            tpl = json.load(f)
        self.assertEqual(tpl.get("version"), "1.1")

        # 5. src-tauri/tauri.conf.json
        tauri_path = os.path.join(project_root, "src-tauri", "tauri.conf.json")
        with open(tauri_path, "r", encoding="utf-8") as f:
            tauri_cfg = json.load(f)
        self.assertEqual(tauri_cfg.get("version"), "1.1")

        # 6. src/welcome.html badge szöveg
        welcome_path = os.path.join(project_root, "src", "welcome.html")
        with open(welcome_path, "r", encoding="utf-8") as f:
            welcome_content = f.read()
        self.assertIn('>v1.1</span>', welcome_content)


class TestUnreadCountExtraction(unittest.TestCase):
    """Ellenőrzi a valós olvasatlan számláló kinyerését és a hamis pozitívok kizárását."""

    def test_valid_unread_patterns(self):
        # Cím legelején lévő zárójeles számok
        self.assertEqual(extract_unread_count("(3) Gmail - maci@gmail.com"), 3)
        self.assertEqual(extract_unread_count("*(1) Google Chat"), 1)
        self.assertEqual(extract_unread_count("[5] Slack | dev-channel"), 5)
        self.assertEqual(extract_unread_count("(99+) WhatsApp"), 99)
        self.assertEqual(extract_unread_count("(12) Messenger"), 12)

        # Mappa/szolgáltatás neve utáni zárójeles számok
        self.assertEqual(extract_unread_count("Gmail — Beérkező levelek (12)"), 12)
        self.assertEqual(extract_unread_count("Inbox (7) - Work Mail"), 7)
        self.assertEqual(extract_unread_count("Beérkező levelek (4) - Gmail"), 4)
        self.assertEqual(extract_unread_count("Beérkezett üzenetek (2) - Outlook"), 2)

        # Cím legvégén lévő csevegő számlálók
        self.assertEqual(extract_unread_count("Telegram (5)"), 5)
        self.assertEqual(extract_unread_count("Telegram Web (3)"), 3)
        self.assertEqual(extract_unread_count("Slack (2)"), 2)
        self.assertEqual(extract_unread_count("Discord (8)"), 8)

    def test_no_false_positives(self):
        # Üres vagy szám nélküli címek
        self.assertEqual(extract_unread_count(""), 0)
        self.assertEqual(extract_unread_count("WhatsApp"), 0)
        self.assertEqual(extract_unread_count("Telegram"), 0)
        self.assertEqual(extract_unread_count("Beérkező levelek - felhasznalo@gmail.com - Gmail"), 0)
        self.assertEqual(extract_unread_count("Slack | General"), 0)

        # Levél tárgyában lévő dátumok, verziók és sorszámok nem téveszthetik meg a számlálót
        self.assertEqual(extract_unread_count("Megbeszélés jegyzőkönyv (2026.10.28)"), 0)
        self.assertEqual(extract_unread_count("Éves pénzügyi beszámoló (2025)"), 0)
        self.assertEqual(extract_unread_count("Hírlevél (1. rész) - Technológiai hírek"), 0)
        self.assertEqual(extract_unread_count("Fontos teendők (12 pontban)"), 0)
        self.assertEqual(extract_unread_count("Projekt dokumentáció (v1.2)"), 0)

    def test_template_initial_unread_zero(self):
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        tpl_path = os.path.join(project_root, "data", "config.json.template")
        with open(tpl_path, "r", encoding="utf-8") as f:
            tpl = json.load(f)
        for tab in tpl.get("tabs", []):
            self.assertEqual(tab.get("unreadCount", 0), 0, f"A(z) {tab.get('id')} fül alapértelmezett számlálója nem 0")


if __name__ == "__main__":
    unittest.main()
