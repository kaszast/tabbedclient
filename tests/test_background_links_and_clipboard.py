#!/usr/bin/env python3
"""
Egységtesztek a háttérben történő linkmegnyitáshoz (Ctrl+bal klikk / középső gomb),
valamint a fülbe történő kép- és fájlbeillesztéshez (Clipboard és DND támogatás).
"""

import base64
import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from desktop.tabbedclient import (
    TabbedClientWindow,
    DEFAULT_CONFIG,
    extract_real_target_url,
    is_external_link,
)


class TestBackgroundLinksAndClipboard(unittest.TestCase):

    def setUp(self):
        self.app = TabbedClientWindow.__new__(TabbedClientWindow)
        self.app.config = {
            "tabs": [
                {"id": "tab-messenger", "title": "Messenger", "url": "https://www.messenger.com/"},
                {"id": "tab-gmail", "title": "Gmail", "url": "https://mail.google.com/"}
            ],
            "activeTabId": "tab-messenger",
            "settings": {}
        }
        self.app.tab_webviews = {}
        self.app.webviews = {}

    def test_open_external_uri_background_flag(self):
        """Teszteli, hogy az open_external_uri in_background=True esetén meghívja a fókusz-megtartást."""
        with patch.object(self.app, "_keep_window_focused") as mock_keep_focus:
            with patch("desktop.tabbedclient.Gio.AppInfo.launch_default_for_uri", return_value=True):
                self.app.open_external_uri("https://example.com/page", in_background=True)
                mock_keep_focus.assert_called_once()

    def test_open_external_uri_foreground_flag(self):
        """Teszteli, hogy az open_external_uri in_background=False esetén NEM hívja a fókusz-megtartást."""
        with patch.object(self.app, "_keep_window_focused") as mock_keep_focus:
            with patch("desktop.tabbedclient.Gio.AppInfo.launch_default_for_uri", return_value=True):
                self.app.open_external_uri("https://example.com/page", in_background=False)
                mock_keep_focus.assert_not_called()

    def test_bg_link_message_triggers_background_open(self):
        """Teszteli, hogy a JavaScript UserScriptből érkező tabbedclient_bg_link üzenet a háttérben nyitja a linket."""
        mock_js_result = MagicMock()
        mock_val = MagicMock()
        mock_val.is_string.return_value = True
        mock_val.to_string.return_value = "https://github.com/torvalds/linux"
        mock_js_result.get_js_value.return_value = mock_val

        with patch.object(self.app, "open_external_uri") as mock_open:
            self.app._on_bg_link_message(None, mock_js_result)
            mock_open.assert_called_once_with("https://github.com/torvalds/linux", in_background=True)

    def test_clipboard_file_data_extraction_from_file_uri(self):
        """Teszteli a fájlkezelőből kimásolt fájl-URI (pl. kep.png) base64 és MIME feldolgozását."""
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tf:
            tf.write(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDRtestimagebytes")
            tf_path = tf.name

        try:
            mock_clipboard = MagicMock()
            mock_clipboard.wait_is_image_available.return_value = False
            mock_clipboard.wait_for_uris.return_value = [f"file://{tf_path}"]

            with patch("desktop.tabbedclient.Gtk.Clipboard.get", return_value=mock_clipboard):
                data = self.app._get_clipboard_image_or_file_data()
                self.assertIsNotNone(data)
                self.assertEqual(data["type"], "image/png")
                self.assertEqual(data["filename"], os.path.basename(tf_path))
                decoded = base64.b64decode(data["data"])
                self.assertTrue(decoded.startswith(b"\x89PNG"))
        finally:
            if os.path.exists(tf_path):
                os.unlink(tf_path)

    def test_clipboard_returns_none_for_plain_text(self):
        """Teszteli, hogy sima szöveges vágólap esetén a segédfüggvény None-t ad vissza a natív beillesztés megőrzéséhez."""
        mock_clipboard = MagicMock()
        mock_clipboard.wait_is_image_available.return_value = False
        mock_clipboard.wait_for_uris.return_value = None

        with patch("desktop.tabbedclient.Gtk.Clipboard.get", return_value=mock_clipboard):
            data = self.app._get_clipboard_image_or_file_data()
            self.assertIsNone(data)

    def test_inject_clipboard_file_to_webview_runs_javascript(self):
        """Teszteli, hogy a szintetikus paste eseményt generáló JavaScript elküldésre kerül a WebView felé."""
        mock_wv = MagicMock()
        file_info = {
            "type": "image/png",
            "filename": "minta.png",
            "data": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        }

        self.app._inject_clipboard_file_to_webview(mock_wv, file_info)
        mock_wv.run_javascript.assert_called_once()
        js_arg = mock_wv.run_javascript.call_args[0][0]
        self.assertIn("minta.png", js_arg)
        self.assertIn("image/png", js_arg)
        self.assertIn("ClipboardEvent('paste'", js_arg)
        self.assertIn("DragEvent('drop'", js_arg)


if __name__ == "__main__":
    unittest.main()
