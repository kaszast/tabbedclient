#!/usr/bin/env python3
"""
Egységtesztek az egypéldányos (single-instance) futás és a fülönkénti nagyítás (zoom level) megjegyzéséhez.
"""

import os
import socket
import tempfile
import time
import unittest

from desktop.tabbedclient import (
    load_config,
    save_config,
    get_instance_socket_path,
    try_activate_existing_instance,
    setup_single_instance_server,
)


class TestZoomPersistence(unittest.TestCase):

    def test_tab_zoom_level_normalization(self):
        # Teszteljük a zoomLevel mező normalizálását a konfigurációban
        from desktop.tabbedclient import DEFAULT_CONFIG
        import copy

        cfg = copy.deepcopy(DEFAULT_CONFIG)
        cfg["tabs"] = [
            {
                "id": "tab-test-1",
                "title": "Teszt 1",
                "url": "https://example.com/1",
                "zoomLevel": 1.25
            },
            {
                "id": "tab-test-2",
                "title": "Teszt 2",
                "url": "https://example.com/2"
                # Nincs zoomLevel -> alapértelmezett 1.0
            },
            {
                "id": "tab-test-3",
                "title": "Teszt 3",
                "url": "https://example.com/3",
                "zoomLevel": 999.0  # Túl nagy -> 1.0 fallback
            }
        ]

        with tempfile.NamedTemporaryFile("w+", suffix=".json", delete=False) as tf:
            import json
            json.dump(cfg, tf)
            tf_path = tf.name

        try:
            # Ideiglenesen felülírjuk a CONFIG_PATH-t
            import desktop.tabbedclient as tc
            orig_path = tc.CONFIG_PATH
            tc.CONFIG_PATH = tf_path

            loaded = load_config()
            tabs = {t["id"]: t for t in loaded["tabs"]}

            self.assertAlmostEqual(tabs["tab-test-1"]["zoomLevel"], 1.25)
            self.assertAlmostEqual(tabs["tab-test-2"]["zoomLevel"], 1.0)
            self.assertAlmostEqual(tabs["tab-test-3"]["zoomLevel"], 1.0)

            # Mentés ellenőrzése új zoomLevel értékkel
            tabs["tab-test-1"]["zoomLevel"] = 1.40
            save_config(loaded)

            reloaded = load_config()
            reloaded_tabs = {t["id"]: t for t in reloaded["tabs"]}
            self.assertAlmostEqual(reloaded_tabs["tab-test-1"]["zoomLevel"], 1.40)
        finally:
            tc.CONFIG_PATH = orig_path
            if os.path.exists(tf_path):
                os.unlink(tf_path)


class TestSingleInstance(unittest.TestCase):

    def test_single_instance_socket_activation(self):
        # Teszteljük a helyi socket-alapú egypéldányos aktiválást
        with tempfile.TemporaryDirectory() as tmpdir:
            test_sock = os.path.join(tmpdir, "test_app.sock")

            # 1. Ha nem fut a szerver, a try_activate_existing_instance sikertelen
            import desktop.tabbedclient as tc
            orig_sock_fn = tc.get_instance_socket_path
            tc.get_instance_socket_path = lambda: test_sock

            try:
                self.assertFalse(try_activate_existing_instance())

                # 2. Elindítjuk a szervert egy aktiválási számlálóval
                activated = []
                def on_activate():
                    activated.append(True)

                server = setup_single_instance_server(on_activate)
                self.assertIsNotNone(server)
                self.assertTrue(os.path.exists(test_sock))

                # 3. Második példány próbálkozása: sikeresen aktivál és True-val tér vissza
                res = try_activate_existing_instance()
                self.assertTrue(res, "A futó példány felé küldött aktiválásnak sikeresnek kell lennie!")

                # Kis várakozás a GLib / socket feldolgozásra
                from gi.repository import GLib
                ctx = GLib.MainContext.default()
                for _ in range(10):
                    ctx.iteration(False)
                    time.sleep(0.01)

                self.assertTrue(len(activated) > 0, "A meglévő példány aktiválási callbackje le kell fusson!")

                server.close()
                if os.path.exists(test_sock):
                    os.unlink(test_sock)
            finally:
                tc.get_instance_socket_path = orig_sock_fn


if __name__ == "__main__":
    unittest.main()
