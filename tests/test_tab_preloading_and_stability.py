#!/usr/bin/env python3
"""
Egységtesztek a Telegram témaváltási stabilitáshoz (close szignál, tg:// protokoll)
és az induláskori rendezett fül-előtöltéshez.
"""

import unittest

from desktop.tabbedclient import (
    SERVICE_EQUIVALENT_GROUPS,
    are_domains_same_service,
    is_external_link,
)


class TestTelegramAndTabPreloading(unittest.TestCase):

    def test_telegram_service_group(self):
        # A Telegram és a t.me ugyanabba a szolgáltatáscsoportba kell tartozzon
        self.assertTrue(are_domains_same_service("web.telegram.org", "t.me"))
        self.assertTrue(are_domains_same_service("web.telegram.org", "telegram.org"))
        self.assertTrue(are_domains_same_service("t.me", "telegra.ph"))

    def test_telegram_theme_links_are_internal(self):
        telegram_tab = "https://web.telegram.org/k/"

        # Belső Telegram témalinkeik és t.me hivatkozások
        self.assertFalse(is_external_link(telegram_tab, "https://t.me/addtheme/classic"))
        self.assertFalse(is_external_link(telegram_tab, "https://web.telegram.org/k/#theme"))
        self.assertFalse(is_external_link(telegram_tab, "tg://theme?slug=custom_dark"))
        self.assertFalse(is_external_link(telegram_tab, "tg://settings"))

        # Valódi külső hivatkozások Telegram csevegésből
        self.assertTrue(is_external_link(telegram_tab, "https://github.com/torvalds/linux"))
        self.assertTrue(is_external_link(telegram_tab, "https://telex.hu"))

    def test_ordered_tab_sorting(self):
        # Fülek sorbarendezése az order mező szerint
        unordered_tabs = [
            {"id": "tab-3", "title": "Harmadik", "order": 3},
            {"id": "tab-0", "title": "Nulladik", "order": 0},
            {"id": "tab-2", "title": "Második", "order": 2},
            {"id": "tab-1", "title": "Első", "order": 1},
        ]
        ordered = sorted(unordered_tabs, key=lambda t: int(t.get("order", 0)))
        ordered_ids = [t["id"] for t in ordered]
        self.assertEqual(ordered_ids, ["tab-0", "tab-1", "tab-2", "tab-3"])

    def test_webview_close_handler_exists(self):
        from desktop.tabbedclient import TabbedClientWindow
        self.assertTrue(hasattr(TabbedClientWindow, "_on_webview_close"))
        self.assertTrue(hasattr(TabbedClientWindow, "_on_web_process_terminated"))


if __name__ == "__main__":
    unittest.main()
