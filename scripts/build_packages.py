#!/usr/bin/env python3
"""
TabbedClient — Automata Csomagkészítő Script (Linux .deb + .tar.gz és Windows .zip)
"""

import os
import shutil
import stat
import subprocess
import sys
import zipfile
import tarfile

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST_DIR = os.path.join(BASE_DIR, "dist")
BUILD_TMP = os.path.join(DIST_DIR, "build_tmp")


def get_project_version() -> str:
    """Kiolvassa a verziószámot a package.json-ból, szinkronban tartva az építőszkripteket."""
    pkg_path = os.path.join(BASE_DIR, "package.json")
    if os.path.exists(pkg_path):
        try:
            with open(pkg_path, "r", encoding="utf-8") as f:
                import json
                data = json.load(f)
                v = data.get("version")
                if v:
                    return str(v).strip()
        except Exception:
            pass
    return "1.1"


VERSION = get_project_version()


def clean_dir(path):
    if os.path.exists(path):
        shutil.rmtree(path)
    os.makedirs(path, exist_ok=True)


def copy_project_data(dest_data_dir):
    os.makedirs(dest_data_dir, exist_ok=True)
    profiles_dir = os.path.join(dest_data_dir, "profiles")
    os.makedirs(profiles_dir, exist_ok=True)
    for p in ("default", "work", "personal"):
        os.makedirs(os.path.join(profiles_dir, p), exist_ok=True)
    src_cfg = os.path.join(BASE_DIR, "data", "config.json.template")
    if not os.path.exists(src_cfg):
        src_cfg = os.path.join(BASE_DIR, "data", "config.json")
    if os.path.exists(src_cfg):
        shutil.copy2(src_cfg, os.path.join(dest_data_dir, "config.json"))


def build_linux_deb():
    print("[1/3] Linux .deb telepítőcsomag készítése...")
    deb_root = os.path.join(BUILD_TMP, "deb")
    clean_dir(deb_root)

    # 1. Könyvtárstruktúra
    debian_dir = os.path.join(deb_root, "DEBIAN")
    bin_dir = os.path.join(deb_root, "usr", "bin")
    app_share_dir = os.path.join(deb_root, "usr", "share", "tabbedclient")
    desktop_dir = os.path.join(deb_root, "usr", "share", "applications")
    pixmaps_dir = os.path.join(deb_root, "usr", "share", "pixmaps")
    hicolor_root = os.path.join(deb_root, "usr", "share", "icons", "hicolor")

    for d in (debian_dir, bin_dir, app_share_dir, desktop_dir, pixmaps_dir, hicolor_root):
        os.makedirs(d, exist_ok=True)

    # Minden szabványos ikonkészlet méret könyvtára
    for sz in (16, 24, 32, 48, 64, 128, 256, 512):
        os.makedirs(os.path.join(hicolor_root, f"{sz}x{sz}", "apps"), exist_ok=True)
    os.makedirs(os.path.join(hicolor_root, "scalable", "apps"), exist_ok=True)

    # 2. DEBIAN/control
    control_content = f"""Package: tabbedclient
Version: {VERSION}
Section: net
Priority: optional
Architecture: all
Depends: python3, python3-gi, gir1.2-gtk-3.0, gir1.2-webkit2-4.1
Recommends: gir1.2-ayatanaappindicator3-0.1, gir1.2-notify-0.7
Maintainer: TabbedClient Team <info@tabbedclient.local>
Description: Zero-telemetry multi-account tabbed web client
 TabbedClient is an isolated, vertical-tab web client with local-only
 storage, multi-account session partitioning and system tray integration.
"""
    control_file = os.path.join(debian_dir, "control")
    with open(control_file, "w", encoding="utf-8") as f:
        f.write(control_content)

    os.chmod(deb_root, 0o755)
    os.chmod(debian_dir, 0o755)
    os.chmod(control_file, 0o644)

    # 3. Forrásfájlok másolása
    shutil.copytree(os.path.join(BASE_DIR, "src"), os.path.join(app_share_dir, "src"))
    shutil.copytree(
        os.path.join(BASE_DIR, "desktop"),
        os.path.join(app_share_dir, "desktop"),
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc")
    )
    shutil.copytree(os.path.join(BASE_DIR, "src-tauri", "icons"), os.path.join(app_share_dir, "icons"))
    copy_project_data(os.path.join(app_share_dir, "data"))

    # 4. /usr/bin/tabbedclient indítófájl
    launcher_path = os.path.join(bin_dir, "tabbedclient")
    with open(launcher_path, "w", encoding="utf-8") as f:
        f.write("""#!/bin/sh
exec /usr/bin/python3 /usr/share/tabbedclient/desktop/tabbedclient.py "$@"
""")
    os.chmod(launcher_path, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)

    # 5. .desktop fájl
    desktop_content = """[Desktop Entry]
Name=TabbedClient
Comment=Zero-telemetry multi-tab web client with partition isolation
Exec=/usr/bin/tabbedclient
Icon=tabbedclient
Terminal=false
Type=Application
Categories=Network;WebBrowser;Chat;
StartupNotify=true
StartupWMClass=tabbedclient
"""
    with open(os.path.join(desktop_dir, "tabbedclient.desktop"), "w", encoding="utf-8") as f:
        f.write(desktop_content)

    # 6. Ikonok másolása minden felbontásban (Hicolor és Pixmaps)
    icons_src_dir = os.path.join(BASE_DIR, "src-tauri", "icons")
    for sz in (16, 24, 32, 48, 64, 128, 256, 512):
        fname = f"{sz}x{sz}.png" if sz != 512 else "icon.png"
        src = os.path.join(icons_src_dir, fname)
        if os.path.exists(src):
            dst = os.path.join(hicolor_root, f"{sz}x{sz}", "apps", "tabbedclient.png")
            shutil.copy2(src, dst)

    src_svg = os.path.join(icons_src_dir, "icon.svg")
    if os.path.exists(src_svg):
        shutil.copy2(src_svg, os.path.join(hicolor_root, "scalable", "apps", "tabbedclient.svg"))

    src_main = os.path.join(icons_src_dir, "icon.png")
    if os.path.exists(src_main):
        shutil.copy2(src_main, os.path.join(pixmaps_dir, "tabbedclient.png"))

    # 7. DEBIAN/postinst és postrm (Desktop adatbázis és ikongyorsítótár frissítés)
    postinst_content = """#!/bin/sh
set -e
if which update-desktop-database >/dev/null 2>&1; then
    update-desktop-database -q /usr/share/applications || true
fi
if which gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache -q -t -f /usr/share/icons/hicolor || true
fi
"""
    postinst_file = os.path.join(debian_dir, "postinst")
    with open(postinst_file, "w", encoding="utf-8") as f:
        f.write(postinst_content)
    os.chmod(postinst_file, 0o755)

    postrm_file = os.path.join(debian_dir, "postrm")
    with open(postrm_file, "w", encoding="utf-8") as f:
        f.write(postinst_content)
    os.chmod(postrm_file, 0o755)

    # 8. Jogosultságok egységesítése
    for root, dirs, files in os.walk(deb_root):
        for d in dirs:
            os.chmod(os.path.join(root, d), 0o755)
        for f in files:
            p = os.path.join(root, f)
            if p in (postinst_file, postrm_file, launcher_path):
                os.chmod(p, 0o755)
            elif not (os.stat(p).st_mode & stat.S_IXUSR):
                os.chmod(p, 0o644)

    # 9. dpkg-deb csomagolás
    deb_output = os.path.join(DIST_DIR, f"tabbedclient_{VERSION}_all.deb")
    res = subprocess.run(["dpkg-deb", "--build", "--root-owner-group", deb_root, deb_output], capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"dpkg-deb hiba: {res.stderr}")
    print(f"✓ Létrehozva: {deb_output} ({os.path.getsize(deb_output):,} bájt)")


def build_linux_tar():
    print("[2/3] Linux hordozható .tar.gz csomag készítése...")
    archive_name = f"tabbedclient-{VERSION}-linux-x86_64.tar.gz"
    out_tar = os.path.join(DIST_DIR, archive_name)

    tar_tmp = os.path.join(BUILD_TMP, f"tabbedclient-{VERSION}-linux")
    clean_dir(tar_tmp)

    # Fájlok összekészítése
    shutil.copy2(os.path.join(BASE_DIR, "tabbedclient"), os.path.join(tar_tmp, "tabbedclient"))
    shutil.copy2(os.path.join(BASE_DIR, "install_desktop_entry.sh"), os.path.join(tar_tmp, "install_desktop_entry.sh"))
    os.makedirs(os.path.join(tar_tmp, "scripts"), exist_ok=True)
    shutil.copy2(os.path.join(BASE_DIR, "scripts", "install_desktop.py"), os.path.join(tar_tmp, "scripts", "install_desktop.py"))
    shutil.copytree(
        os.path.join(BASE_DIR, "desktop"),
        os.path.join(tar_tmp, "desktop"),
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc")
    )
    shutil.copytree(os.path.join(BASE_DIR, "src"), os.path.join(tar_tmp, "src"))
    shutil.copytree(os.path.join(BASE_DIR, "src-tauri", "icons"), os.path.join(tar_tmp, "src-tauri", "icons"))
    copy_project_data(os.path.join(tar_tmp, "data"))

    readme_content = """TabbedClient — Hordozható Linux Csomag
=======================================

Indítás közvetlenül hordozhatóként:
    ./tabbedclient

Tálcára kitűzés és menüintegráció (Zorin OS / Ubuntu / GNOME / KDE):
    ./install_desktop_entry.sh
    (Ez azonnal regisztrálja a Bento ikont az asztali környezetben és lehetővé teszi a jobb-klikkes 'Kitűzés a tálcára' opciót.)

Rendszerkövetelmények (Debian / Ubuntu / Zorin OS / Mint):
    sudo apt install python3-gi gir1.2-gtk-3.0 gir1.2-webkit2-4.1 gir1.2-ayatanaappindicator3-0.1
"""
    with open(os.path.join(tar_tmp, "README.txt"), "w", encoding="utf-8") as f:
        f.write(readme_content)

    with tarfile.open(out_tar, "w:gz") as tar:
        tar.add(tar_tmp, arcname=f"tabbedclient-{VERSION}")

    print(f"✓ Létrehozva: {out_tar} ({os.path.getsize(out_tar):,} bájt)")


def build_windows_zip():
    print("[3/3] Windows hordozható .zip csomag készítése...")
    zip_name = f"tabbedclient-{VERSION}-windows.zip"
    out_zip = os.path.join(DIST_DIR, zip_name)

    win_tmp = os.path.join(BUILD_TMP, f"tabbedclient-{VERSION}-windows")
    clean_dir(win_tmp)

    # Windows indítófájlok
    shutil.copy2(os.path.join(BASE_DIR, "TabbedClient.bat"), os.path.join(win_tmp, "TabbedClient.bat"))
    shutil.copy2(os.path.join(BASE_DIR, "TabbedClient.vbs"), os.path.join(win_tmp, "TabbedClient.vbs"))
    shutil.copy2(os.path.join(BASE_DIR, "TabbedClient.ps1"), os.path.join(win_tmp, "TabbedClient.ps1"))
    shutil.copytree(
        os.path.join(BASE_DIR, "desktop"),
        os.path.join(win_tmp, "desktop"),
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc")
    )
    shutil.copytree(os.path.join(BASE_DIR, "src"), os.path.join(win_tmp, "src"))
    shutil.copytree(os.path.join(BASE_DIR, "src-tauri", "icons"), os.path.join(win_tmp, "src-tauri", "icons"))
    shutil.copy2(os.path.join(BASE_DIR, "src-tauri", "icons", "icon.ico"), os.path.join(win_tmp, "TabbedClient.ico"))
    copy_project_data(os.path.join(win_tmp, "data"))

    readme_win = """TabbedClient — Hordozható Windows Csomag
========================================

Indítás Windows alatt:
1. Kattints duplán a TabbedClient.vbs fájlra (csendes indítás, fekete parancssor nélkül).
VAGY:
2. Kattints duplán a TabbedClient.bat fájlra.

Működés:
- Ha telepítve van a Python (3.9+), a program közvetlenül fut.
- Ha nincs Python, automatikusan a Windows beépített Microsoft Edge App Mode böngészőjét indítja el külön elszeparált adatprofilokkal.
- Semmilyen telepítés vagy rendszergazdai jogosultság nem szükséges!
"""
    with open(os.path.join(win_tmp, "README_WINDOWS.txt"), "w", encoding="utf-8") as f:
        f.write(readme_win)

    with zipfile.ZipFile(out_zip, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(win_tmp):
            for file in files:
                abs_path = os.path.join(root, file)
                rel_path = os.path.relpath(abs_path, win_tmp)
                zipf.write(abs_path, os.path.join(f"tabbedclient-{VERSION}-windows", rel_path))

    print(f"✓ Létrehozva: {out_zip} ({os.path.getsize(out_zip):,} bájt)")


def main():
    os.makedirs(DIST_DIR, exist_ok=True)
    build_linux_deb()
    build_linux_tar()
    build_windows_zip()
    # Ideiglenes fájlok takarítása
    if os.path.exists(BUILD_TMP):
        shutil.rmtree(BUILD_TMP)
    print("\n[SIKER] Minden csomag sikeresen elkészült a dist/ mappában.")


if __name__ == "__main__":
    main()
