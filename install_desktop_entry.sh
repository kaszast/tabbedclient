#!/bin/sh
# TabbedClient - Asztali indító és ikonok regisztrálása a felhasználói profilba
# (Zorin OS, Ubuntu, Debian, GNOME, KDE, XFCE tálca- és menüintegráció)

set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
exec /usr/bin/python3 "$SCRIPT_DIR/scripts/install_desktop.py" "$@"
