import os
import sys
import shutil
import subprocess

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_ICONS = os.path.join(BASE_DIR, "src-tauri", "icons")

def install_user_desktop_integration(silent=False):
    """
    Regisztrálja a TabbedClient alkalmazást a felhasználói XDG könyvtárakban
    (~/.local/share/applications és ~/.local/share/icons), így GNOME Shell / Zorin OS alatt
    azonnal megjelenik a menüben, láthatóvá válik a tálca-ikon, és kitűzhetővé válik a tálcára.
    """
    try:
        user_apps = os.path.expanduser("~/.local/share/applications")
        user_icons = os.path.expanduser("~/.local/share/icons/hicolor")
        user_pixmaps = os.path.expanduser("~/.local/share/pixmaps")

        # 1. Könyvtárak létrehozása
        for p in (user_apps, user_icons, user_pixmaps):
            os.makedirs(p, exist_ok=True)

        # 2. Ikonok másolása minden szabványos méretben
        sizes = [16, 24, 32, 48, 64, 128, 256, 512]
        for sz in sizes:
            sz_dir = os.path.join(user_icons, f"{sz}x{sz}", "apps")
            os.makedirs(sz_dir, exist_ok=True)
            fname = f"{sz}x{sz}.png" if sz != 512 else "icon.png"
            src = os.path.join(SRC_ICONS, fname)
            if os.path.exists(src):
                shutil.copy2(src, os.path.join(sz_dir, "tabbedclient.png"))

        # Skálázható SVG ikon
        scalable_dir = os.path.join(user_icons, "scalable", "apps")
        os.makedirs(scalable_dir, exist_ok=True)
        svg_src = os.path.join(SRC_ICONS, "icon.svg")
        if os.path.exists(svg_src):
            shutil.copy2(svg_src, os.path.join(scalable_dir, "tabbedclient.svg"))

        # Pixmaps közvetlen fallback ikon
        main_icon = os.path.join(SRC_ICONS, "icon.png")
        if os.path.exists(main_icon):
            shutil.copy2(main_icon, os.path.join(user_pixmaps, "tabbedclient.png"))

        # 3. Indítófájl elérési útja
        launcher_bin = os.path.join(BASE_DIR, "tabbedclient")
        if not os.path.exists(launcher_bin) or not os.access(launcher_bin, os.X_OK):
            # Fallback a python futtatóra
            launcher_bin = f"/usr/bin/python3 {os.path.join(BASE_DIR, 'desktop', 'tabbedclient.py')}"

        desktop_file_path = os.path.join(user_apps, "tabbedclient.desktop")

        desktop_content = f"""[Desktop Entry]
Version=1.0
Type=Application
Name=TabbedClient
GenericName=Multi-Account Web Kliens
Comment=Zero-telemetry multi-account tabbed web client with partition isolation
Exec={launcher_bin} %U
Icon=tabbedclient
Terminal=false
Categories=Network;WebBrowser;Chat;
StartupNotify=true
StartupWMClass=tabbedclient
MimeType=x-scheme-handler/http;x-scheme-handler/https;
Keywords=web;browser;chat;tabs;slack;gmail;discord;messenger;zorin;
Actions=NewTab;

[Desktop Action NewTab]
Name=Új fül hozzáadása
Exec={launcher_bin}
"""
        with open(desktop_file_path, "w", encoding="utf-8") as f:
            f.write(desktop_content)
        os.chmod(desktop_file_path, 0o755)

        # 4. Asztali adatbázis és ikongyorsítótár frissítése
        if shutil.which("update-desktop-database"):
            subprocess.run(["update-desktop-database", user_apps], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if shutil.which("gtk-update-icon-cache"):
            subprocess.run(["gtk-update-icon-cache", "-q", "-t", "-f", user_icons], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        if not silent:
            print(f"✓ TabbedClient asztali integráció sikeresen telepítve: {desktop_file_path}")
            print(f"✓ Ikonok regisztrálva: {user_icons}")
        return True
    except Exception as err:
        if not silent:
            print(f"[Desktop Integráció Figyelmeztetés] {err}", file=sys.stderr)
        return False

if __name__ == "__main__":
    success = install_user_desktop_integration(silent=False)
    sys.exit(0 if success else 1)
