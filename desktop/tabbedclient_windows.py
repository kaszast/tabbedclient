#!/usr/bin/env python3
"""
TabbedClient — Windows Futtató és Indító Modul
Támogatja a natív Microsoft Edge App Mode-ot, WebView2-t és a helyi adatprofilokat.
"""

import json
import os
import subprocess
import sys
import webbrowser

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(BASE_DIR, "src")
DATA_DIR = os.path.join(BASE_DIR, "data")
PROFILES_DIR = os.path.join(DATA_DIR, "profiles")
CONFIG_PATH = os.path.join(DATA_DIR, "config.json")

os.makedirs(PROFILES_DIR, exist_ok=True)


def find_windows_edge():
    """Megkeresi a Microsoft Edge futtatható állományát Windows alatt."""
    possible_paths = [
        os.path.expandvars(r"%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"),
        os.path.expandvars(r"%ProgramFiles%\Microsoft\Edge\Application\msedge.exe"),
        os.path.expandvars(r"%LocalAppData%\Microsoft\Edge\Application\msedge.exe"),
    ]
    for p in possible_paths:
        if os.path.isfile(p):
            return p
    return None


def run_windows():
    # 1. Próbálkozás pywebview (WebView2) használatával, ha telepítve van
    try:
        import webview
        index_file = os.path.join(SRC_DIR, "index.html")
        webview.create_window(
            title="TabbedClient",
            url=f"file:///{os.path.abspath(index_file).replace(os.sep, '/')}",
            width=1280,
            height=840,
            min_size=(400, 500)
        )
        webview.start(private_mode=False)
        return
    except ImportError:
        pass

    # 2. Próbálkozás natív Microsoft Edge App Mode indítással
    edge_exe = find_windows_edge()
    index_url = f"file:///{os.path.abspath(os.path.join(SRC_DIR, 'index.html')).replace(os.sep, '/')}"
    user_data_dir = os.path.abspath(os.path.join(PROFILES_DIR, "default"))

    if edge_exe and os.path.isfile(edge_exe):
        cmd = [
            edge_exe,
            f"--app={index_url}",
            f"--user-data-dir={user_data_dir}",
            "--no-first-run",
            "--disable-sync",
            "--disable-telemetry",
            "--window-size=1280,840"
        ]
        try:
            subprocess.Popen(cmd)
            return
        except Exception as err:
            print(f"[WARN] Edge indítás sikertelen: {err}", file=sys.stderr)

    # 3. Fallback: alapértelmezett böngésző megnyitása az index.html felületre
    print("[INFO] Megnyitás az alapértelmezett böngészőben...")
    webbrowser.open(index_url)


if __name__ == "__main__":
    run_windows()
