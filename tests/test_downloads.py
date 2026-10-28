#!/usr/bin/env python3
"""
Egységtesztek a letöltéskezelőhöz (csatolmányok, képek, blob/data URL-ek letöltése és mentése).
"""

import base64
import json
import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from desktop.tabbedclient import (
    TabbedClientWindow,
)


class TestDownloads(unittest.TestCase):

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

    def test_sanitize_filename(self):
        """Teszteli a veszélyes karakterek és könyvtár-átlépések eltávolítását a letöltött fájlnevekből."""
        self.assertEqual(TabbedClientWindow._sanitize_filename("normal_file.pdf"), "normal_file.pdf")
        self.assertEqual(TabbedClientWindow._sanitize_filename("../../etc/passwd"), "passwd")
        self.assertEqual(TabbedClientWindow._sanitize_filename("kép: 2026-10-28?.png"), "kép_ 2026-10-28_.png")
        self.assertEqual(TabbedClientWindow._sanitize_filename(""), "download")
        self.assertEqual(TabbedClientWindow._sanitize_filename(".."), "download")
        self.assertEqual(TabbedClientWindow._sanitize_filename("my%20document%20%281%29.docx"), "my document (1).docx")

    def test_get_unique_filepath_avoids_overwrite(self):
        """Teszteli, hogy azonos nevű fájl esetén (1), (2) indexeléssel egyedi útvonal készül."""
        with tempfile.TemporaryDirectory() as temp_dir:
            orig_file = os.path.join(temp_dir, "report.pdf")
            with open(orig_file, "w") as f:
                f.write("content")

            path1 = TabbedClientWindow._get_unique_filepath(temp_dir, "report.pdf")
            self.assertEqual(os.path.basename(path1), "report (1).pdf")

            with open(path1, "w") as f:
                f.write("content 1")

            path2 = TabbedClientWindow._get_unique_filepath(temp_dir, "report.pdf")
            self.assertEqual(os.path.basename(path2), "report (2).pdf")

    def test_download_decide_destination_sets_valid_uri(self):
        """Teszteli, hogy a WebKit2.Download decide-destination beállítja a cél-URI-t."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.object(self.app, "get_download_dir", return_value=temp_dir):
                mock_download = MagicMock()
                mock_download.get_response.return_value = None
                mock_download.get_request.return_value = None

                res = self.app._on_download_decide_destination(mock_download, "minta_csatolmany.pdf")
                self.assertTrue(res)
                mock_download.set_destination.assert_called_once()
                dest_uri = mock_download.set_destination.call_args[0][0]
                self.assertTrue(dest_uri.startswith("file://"))
                self.assertIn("minta_csatolmany.pdf", dest_uri)
                mock_download.set_allow_overwrite.assert_called_once_with(False)

    def test_blob_download_message_saves_file_and_notifies(self):
        """Teszteli a JavaScriptből érkező blob/data letöltési üzenet dekódolását és lemezre mentését."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.object(self.app, "get_download_dir", return_value=temp_dir):
                with patch.object(self.app, "_show_download_notification") as mock_notif:
                    test_bytes = b"Hello, this is a test image or attachment content."
                    b64_content = base64.b64encode(test_bytes).decode("ascii")
                    data_url = f"data:image/jpeg;base64,{b64_content}"

                    payload = {
                        "filename": "messenger_photo",
                        "dataUrl": data_url,
                        "mimeType": "image/jpeg"
                    }

                    mock_js_result = MagicMock()
                    mock_val = MagicMock()
                    mock_val.is_string.return_value = True
                    mock_val.to_string.return_value = json.dumps(payload)
                    mock_js_result.get_js_value.return_value = mock_val

                    self.app._on_blob_download_message(None, mock_js_result)

                    saved_file = os.path.join(temp_dir, "messenger_photo.jpg")
                    self.assertTrue(os.path.exists(saved_file), f"A fájlnak léteznie kell: {saved_file}")
                    with open(saved_file, "rb") as f:
                        self.assertEqual(f.read(), test_bytes)

                    mock_notif.assert_called_once()
                    self.assertIn("messenger_photo.jpg", mock_notif.call_args[1]["body"])

    def test_response_policy_triggers_download_for_unsupported_mime(self):
        """Teszteli, hogy nem megjeleníthető MIME-típusú HTTP válasz esetén a decide-policy elindítja a letöltést."""
        mock_decision = MagicMock()
        mock_decision.is_mime_type_supported.return_value = False

        from gi.repository import WebKit2
        handled = self.app._on_decide_policy(
            webview=MagicMock(),
            decision=mock_decision,
            decision_type=WebKit2.PolicyDecisionType.RESPONSE,
            tab_id="tab-gmail"
        )
        self.assertTrue(handled)
        mock_decision.download.assert_called_once()

    def test_response_policy_triggers_download_for_attachment_header(self):
        """Teszteli, hogy javasolt fájlnévvel (attachment) rendelkező válasz esetén a decide-policy letöltést indít."""
        mock_decision = MagicMock()
        mock_decision.is_mime_type_supported.return_value = True
        mock_response = MagicMock()
        mock_response.get_suggested_filename.return_value = "szamla.pdf"
        mock_decision.get_response.return_value = mock_response

        from gi.repository import WebKit2
        handled = self.app._on_decide_policy(
            webview=MagicMock(),
            decision=mock_decision,
            decision_type=WebKit2.PolicyDecisionType.RESPONSE,
            tab_id="tab-gmail"
        )
        self.assertTrue(handled)
        mock_decision.download.assert_called_once()


if __name__ == "__main__":
    unittest.main()
