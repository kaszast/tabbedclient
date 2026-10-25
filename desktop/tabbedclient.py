#!/usr/bin/env python3
"""
TabbedClient — Natív Linux GTK3 + WebKitGTK Multi-Tab Kliens
Zero-Telemetry, Teljes Munkamenet-Izoláció (Multi-Account)
"""

import base64
import io
import json
import os
import re
import subprocess
import sys
import urllib.parse
import uuid

# Dual-GPU / Linux WebKit2GTK 2.42+ DMA-BUF inicializációs késleltetés megelőzése
os.environ.setdefault("WEBKIT_DISABLE_DMABUF_RENDERER", "1")

import gi

gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
gi.require_version('Gio', '2.0')
try:
    gi.require_version('WebKit2', '4.1')
except ValueError:
    gi.require_version('WebKit2', '4.0')

try:
    gi.require_version('AyatanaAppIndicator3', '0.1')
    from gi.repository import AyatanaAppIndicator3 as AppIndicator
except Exception:
    try:
        gi.require_version('AppIndicator3', '0.1')
        from gi.repository import AppIndicator3 as AppIndicator
    except Exception:
        AppIndicator = None

try:
    gi.require_version('Notify', '0.7')
    from gi.repository import Notify
except Exception:
    Notify = None

from gi.repository import Gtk, WebKit2, Gdk, GLib, GdkPixbuf, Gio

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(BASE_DIR, "src")
TEMPLATE_CONFIG_PATH = os.path.join(BASE_DIR, "data", "config.json")
if not os.path.exists(TEMPLATE_CONFIG_PATH):
    TEMPLATE_CONFIG_PATH = os.path.join(BASE_DIR, "data", "config.json.template")


def _resolve_paths():
    """
    Meghatározza a konfiguráció, adatprofilok és gyorsítótár elérési útvonalait.
    - Rendszerszintű telepítés (/usr, /opt) esetén szabványos XDG könyvtárakat használ
      (~/.config/tabbedclient és ~/.local/share/tabbedclient), így sosem lép fel jogosultsági hiba (PermissionError).
    - Hordozható (Portable) vagy fejlesztői környezetben, ha a helyi ./data mappa írható,
      akkor a helyi adatkönyvtárat használja.
    """
    is_system_install = BASE_DIR.startswith("/usr") or BASE_DIR.startswith("/opt")
    local_data = os.path.join(BASE_DIR, "data")

    if not is_system_install and os.path.exists(local_data) and os.access(local_data, os.W_OK):
        data_dir = local_data
        config_path = os.path.join(data_dir, "config.json")
        profiles_dir = os.path.join(data_dir, "profiles")
    else:
        xdg_config = os.environ.get("XDG_CONFIG_HOME") or os.path.expanduser("~/.config")
        xdg_data = os.environ.get("XDG_DATA_HOME") or os.path.expanduser("~/.local/share")
        
        config_dir = os.path.join(xdg_config, "tabbedclient")
        data_dir = os.path.join(xdg_data, "tabbedclient")
        profiles_dir = os.path.join(data_dir, "profiles")
        config_path = os.path.join(config_dir, "config.json")

    return data_dir, config_path, profiles_dir


DATA_DIR, CONFIG_PATH, PROFILES_DIR = _resolve_paths()

try:
    os.makedirs(PROFILES_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
except Exception:
    pass

VALID_THEMES = ["slate", "nordic", "jetbrains", "solarized", "enterprise"]
SIDEBAR_EXPANDED_WIDTH = 220
SIDEBAR_COLLAPSED_WIDTH = 48

DEFAULT_CONFIG = {
    "version": "1.0.0",
    "theme": "slate",
    "sidebarCollapsed": False,
    "activeTabId": None,
    "settings": {
        "theme": "slate",
        "sidebarCollapsed": False,
        "minimizeToTrayOnClose": True,
        "startMinimized": False,
        "hardwareAcceleration": True
    },
    "profiles": [
        {"id": "default", "name": "Alapértelmezett", "color": "#94a3b8"},
        {"id": "work", "name": "Munkahelyi", "color": "#388bfd"},
        {"id": "personal", "name": "Magán", "color": "#2ea043"}
    ],
    "tabs": []
}


def _default_favicon_url(url: str) -> str:
    try:
        parts = urllib.parse.urlsplit(url or "")
        if parts.scheme and parts.netloc:
            return f"{parts.scheme}://{parts.netloc}/favicon.ico"
    except Exception:
        pass
    return ""


def extract_real_target_url(target_uri: str) -> str:
    """Kibontja a szolgáltatók által átirányított külső webcímeket (pl. Gmail /url?q=, Messenger l.php?u=)."""
    try:
        parsed = urllib.parse.urlsplit(target_uri)
        netloc = parsed.netloc.lower()
        # Gmail / Google átirányítás
        if "google." in netloc and parsed.path.startswith("/url"):
            qs = urllib.parse.parse_qs(parsed.query)
            if "q" in qs and qs["q"]:
                return qs["q"][0]
            if "url" in qs and qs["url"]:
                return qs["url"][0]
        # Facebook / Messenger átirányítás
        if ("messenger.com" in netloc or "facebook.com" in netloc) and ("l.php" in parsed.path or "l.messenger" in netloc):
            qs = urllib.parse.parse_qs(parsed.query)
            if "u" in qs and qs["u"]:
                return qs["u"][0]
    except Exception:
        pass
    return target_uri


# Kapcsolódó szolgáltatás-domain csoportok (amelyek azonos ökoszisztémát / belső infrastruktúrát képviselnek)
SERVICE_EQUIVALENT_GROUPS = [
    # Meta ökoszisztéma (Facebook, Messenger, WhatsApp, Instagram, Threads, CDN és belső sandbox proxy)
    {
        "facebook.com", "messenger.com", "fbsbx.com", "fbcdn.net",
        "m.me", "whatsapp.com", "whatsapp.net", "meta.com",
        "instagram.com", "threads.net"
    },
    # Google ökoszisztéma (Kereső, Gmail, Naptár, Drive, Docs, YouTube, fiókok és statikus tartalmak)
    {
        "google.com", "google.hu", "gstatic.com", "googleusercontent.com",
        "youtube.com", "youtu.be", "googlevideo.com", "googleapis.com",
        "ggpht.com"
    },
    # Microsoft ökoszisztéma (Outlook, Office, Teams, SharePoint, OneDrive, Live, Skype, Auth)
    {
        "microsoft.com", "live.com", "office.com", "office365.com",
        "sharepoint.com", "outlook.com", "teams.microsoft.com", "skype.com",
        "msftauth.net", "msauth.net", "microsoftonline.com"
    },
    # Slack ökoszisztéma
    {
        "slack.com", "slack-edge.com", "slack-msgs.com", "slack-redir.net"
    },
]


def get_root_domain(host: str) -> str:
    """Kinyeri a regisztrálható fődomaint (pl. www.messenger.com -> messenger.com, sub.google.co.uk -> google.co.uk)."""
    if not host:
        return ""
    host = host.lower().split(":")[0].strip(".")
    parts = host.split(".")
    if len(parts) <= 1:
        return host

    two_part_tlds = ("co.uk", "org.uk", "gov.uk", "com.br", "co.jp", "com.au")
    if len(parts) >= 3 and ".".join(parts[-2:]) in two_part_tlds:
        return ".".join(parts[-3:])

    return ".".join(parts[-2:])


def are_domains_same_service(host_a: str, host_b: str) -> bool:
    """Eldönti, hogy a két domain cím ugyanazon webes szolgáltatás / ökoszisztéma része-e."""
    if not host_a or not host_b:
        return False

    root_a = get_root_domain(host_a)
    root_b = get_root_domain(host_b)

    if root_a and root_a == root_b:
        return True

    for group in SERVICE_EQUIVALENT_GROUPS:
        in_a = any(root_a == item or host_a == item or host_a.endswith("." + item) for item in group)
        in_b = any(root_b == item or host_b == item or host_b.endswith("." + item) for item in group)
        if in_a and in_b:
            return True

    return False


def is_auth_or_login_url(uri: str) -> bool:
    """Meghatározza, hogy az adott webcím bejelentkezési, azonosítási vagy belső szolgáltatás-proxyhoz tartozik-e."""
    try:
        parsed = urllib.parse.urlsplit(uri)
        netloc = parsed.netloc.lower().split(":")[0]
        path = parsed.path.lower()

        # Meta belső MAW (Multi-Account Web) proxy és háttér-kommunikációs végpontok
        if "fbsbx.com" in netloc or "maw_proxy_page" in path:
            return True

        # Ismert hitelesítési és azonosítási szerverek
        auth_hosts = (
            "accounts.google.", "login.microsoftonline.", "login.live.",
            "appleid.apple.", "auth.slack.", "auth0.", "okta.",
            "identity.", "cas.", "sso.", "msftauth.net", "msauth.net"
        )
        if any(h in netloc for h in auth_hosts):
            return True

        # Tipikus OAuth / SSO végpontok
        auth_paths = (
            "/oauth", "/oauth2", "/saml", "/sso", "/login", "/signin",
            "/auth", "/authenticate", "/session", "/checkpoint", "/maw_proxy_page"
        )
        if any(path.startswith(ap) or ap in path for ap in auth_paths):
            return True
    except Exception:
        pass
    return False


def is_external_link(tab_base_url: str, target_uri: str) -> bool:
    """Megvizsgálja, hogy a cél-hivatkozás külső böngészőben nyitandó-e meg a fül alapértelmezett szolgáltatásához képest."""
    try:
        real_target = extract_real_target_url(target_uri)
        parsed_target = urllib.parse.urlsplit(real_target)
        scheme = parsed_target.scheme.lower()

        if not scheme or scheme in ("javascript", "about", "data", "file"):
            return False

        if scheme not in ("http", "https"):
            return True  # mailto:, tel:, magnet: stb.

        # Ha bejelentkezési / OAuth folyamat vagy belső proxy, a fülön belül kell maradnia a süti-izolációhoz
        if is_auth_or_login_url(real_target):
            return False

        parsed_base = urllib.parse.urlsplit(tab_base_url or "")
        base_host = parsed_base.netloc.lower().split(":")[0]
        target_host = parsed_target.netloc.lower().split(":")[0]

        if not base_host:
            return False

        if target_host == base_host:
            return False

        # Ha azonos ökoszisztémához / szolgáltatáshoz tartoznak
        if are_domains_same_service(base_host, target_host):
            # Kivétel: Google /url keresési átirányítás külső célponttal
            if "google." in base_host and "google." in target_host:
                if real_target != target_uri or parsed_target.path.startswith("/url"):
                    return True
            return False

        return True
    except Exception:
        return False


def load_config():
    try:
        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    except Exception:
        pass

    cfg = json.loads(json.dumps(DEFAULT_CONFIG))

    # Ha a felhasználói config még nem létezik, de van sablon (pl. telepített /usr/share csomagban)
    target_path = CONFIG_PATH
    if not os.path.exists(target_path) and os.path.exists(TEMPLATE_CONFIG_PATH):
        target_path = TEMPLATE_CONFIG_PATH

    if os.path.exists(target_path):
        try:
            with open(target_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    cfg["version"] = data.get("version", "1.0.0")
                    if isinstance(data.get("settings"), dict):
                        cfg["settings"].update(data["settings"])
                    if isinstance(data.get("profiles"), list) and len(data["profiles"]) > 0:
                        cfg["profiles"] = data["profiles"]
                    if isinstance(data.get("tabs"), list):
                        cfg["tabs"] = data["tabs"]

                    # Top-level visszamenőleges szinkronizáció
                    if "theme" in data:
                        cfg["theme"] = data["theme"]
                        cfg["settings"]["theme"] = data["theme"]
                    else:
                        cfg["theme"] = cfg["settings"].get("theme", "slate")

                    if "sidebarCollapsed" in data:
                        cfg["sidebarCollapsed"] = data["sidebarCollapsed"]
                        cfg["settings"]["sidebarCollapsed"] = data["sidebarCollapsed"]
                    else:
                        cfg["sidebarCollapsed"] = cfg["settings"].get("sidebarCollapsed", False)

                    cfg["activeTabId"] = data.get("activeTabId")
        except Exception as err:
            print(f"[WARN] Konfiguráció betöltési hiba ({err}), alapértelmezett használata.", file=sys.stderr)

    if cfg["theme"] not in VALID_THEMES:
        cfg["theme"] = "slate"
        cfg["settings"]["theme"] = "slate"

    # Fülek normalizálása
    normalized = []
    for idx, t in enumerate(cfg.get("tabs", [])):
        title = t.get("title") or t.get("name") or "Szolgáltatás"
        profile = t.get("profile") or t.get("profileId") or "default"
        url = t.get("url", "https://example.com")
        normalized.append({
            "id": t.get("id") or f"tab-{uuid.uuid4().hex[:8]}",
            "title": title,
            "name": title,
            "url": url,
            "icon": t.get("icon") or "globe",
            "profile": profile,
            "profileId": profile,
            "notificationsEnabled": bool(t.get("notificationsEnabled", True)),
            "unreadCount": int(t.get("unreadCount", 0)),
            "order": int(t.get("order", idx)),
            "favicon": t.get("favicon") or "",
            "faviconUrl": t.get("faviconUrl") or _default_favicon_url(url)
        })
    # Ha sablonból töltöttük be, és a felhasználói config még nem létezik, mentsük el a felhasználói XDG helyre
    if target_path != CONFIG_PATH and not os.path.exists(CONFIG_PATH):
        try:
            save_config(cfg)
        except Exception:
            pass

    cfg["tabs"] = normalized
    return cfg


def save_config(cfg):
    try:
        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
        os.makedirs(DATA_DIR, exist_ok=True)
        if "settings" not in cfg or not isinstance(cfg["settings"], dict):
            cfg["settings"] = {
                "theme": cfg.get("theme", "slate"),
                "sidebarCollapsed": bool(cfg.get("sidebarCollapsed", False)),
                "minimizeToTrayOnClose": True,
                "startMinimized": False,
                "hardwareAcceleration": True
            }
        # Kétirányú szinkronban tartás a specifikáció és a meglévő kód között
        cfg["theme"] = cfg["settings"].get("theme", cfg.get("theme", "slate"))
        cfg["sidebarCollapsed"] = bool(cfg["settings"].get("sidebarCollapsed", cfg.get("sidebarCollapsed", False)))
        
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2, ensure_ascii=False)
    except Exception as err:
        print(f"[Save Config Error] {err}", file=sys.stderr)


class TabbedClientWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="TabbedClient — Kezdőlap")
        self.set_default_size(1280, 840)
        self.set_position(Gtk.WindowPosition.CENTER)

        GLib.set_prgname("tabbedclient")
        GLib.set_application_name("TabbedClient")
        self.set_role("browser")
        
        # Hivatalos alkalmazás-ikonok beállítása (Bento dizájn multi-resolution lista)
        candidate_icon_dirs = [
            os.path.join(BASE_DIR, "icons"),
            os.path.join(BASE_DIR, "src-tauri", "icons"),
            "/usr/share/tabbedclient/icons",
            "/usr/share/icons/hicolor"
        ]
        icons_dir = next((d for d in candidate_icon_dirs if os.path.exists(d)), "")
        pixbufs = []
        for sz in (16, 24, 32, 48, 64, 128, 256, 512):
            fname = f"{sz}x{sz}.png" if sz != 512 else "icon.png"
            p = os.path.join(icons_dir, fname) if icons_dir else ""
            if not p or not os.path.exists(p):
                p = f"/usr/share/icons/hicolor/{sz}x{sz}/apps/tabbedclient.png"
            if not os.path.exists(p):
                p = f"/usr/share/tabbedclient/icons/{fname}"
            if os.path.exists(p):
                try:
                    pixbufs.append(GdkPixbuf.Pixbuf.new_from_file(p))
                except Exception:
                    pass

        if pixbufs:
            Gtk.Window.set_default_icon_list(pixbufs)
            self.set_icon_list(pixbufs)

        Gtk.Window.set_default_icon_name("tabbedclient")
        self.set_icon_name("tabbedclient")

        # Helyi ikontéma elérési út hozzáadása
        if icons_dir and os.path.exists(icons_dir):
            try:
                theme = Gtk.IconTheme.get_default()
                if theme:
                    theme.append_search_path(icons_dir)
            except Exception:
                pass

        # Automatikus asztali integráció (Zorin OS / GNOME tálca és indító regisztráció)
        try:
            has_system_desktop = os.path.exists("/usr/share/applications/tabbedclient.desktop")
            has_user_desktop = os.path.exists(os.path.expanduser("~/.local/share/applications/tabbedclient.desktop"))
            if not has_system_desktop and not has_user_desktop:
                from scripts.install_desktop import install_user_desktop_integration
                install_user_desktop_integration(silent=True)
        except Exception:
            pass

        self.set_skip_taskbar_hint(False)
        self.set_skip_pager_hint(False)

        if Notify:
            try:
                Notify.init("TabbedClient")
            except Exception as e:
                print(f"[Notify Init Warning] {e}", file=sys.stderr)

        self.config = load_config()
        self.data_managers = {}
        self.contexts = {}
        self.webviews = {}
        self.tab_webviews = {}
        self.previous_tab_id = None
        self.current_welcome_view = "dashboard"
        self._current_sidebar_width = None
        self._last_button_event = None
        self._context_menu = None
        self.tray = None
        self.tray_menu = None

        self.setup_ui()
        self.setup_tray()

        self.connect("delete-event", self.on_window_delete)
        self.connect("window-state-event", self.on_window_state_event)
        self.connect("key-press-event", self._on_window_key_press)

        # startMinimized kezelése
        if self.config.get("settings", {}).get("startMinimized", False) and self.tray:
            self.hide()
        else:
            self.show_all()

    def setup_tray(self):
        if not AppIndicator:
            return
        try:
            candidate_dirs = [
                os.path.join(BASE_DIR, "icons"),
                os.path.join(BASE_DIR, "src-tauri", "icons"),
                "/usr/share/tabbedclient/icons",
                "/usr/share/icons/hicolor/48x48/apps",
                "/usr/share/pixmaps"
            ]
            icon_theme_dir = next((d for d in candidate_dirs if os.path.exists(d)), None)
            icon_name = "tabbedclient"
            if hasattr(AppIndicator.Indicator, "new_with_path") and icon_theme_dir:
                self.tray = AppIndicator.Indicator.new_with_path(
                    "tabbedclient",
                    icon_name,
                    AppIndicator.IndicatorCategory.APPLICATION_STATUS,
                    icon_theme_dir
                )
            else:
                self.tray = AppIndicator.Indicator.new(
                    "tabbedclient",
                    icon_name,
                    AppIndicator.IndicatorCategory.APPLICATION_STATUS
                )
            self.tray.set_status(AppIndicator.IndicatorStatus.ACTIVE)
            self.tray.set_title("TabbedClient")
            self.update_tray_menu()
        except Exception as e:
            print(f"[Tray Init Warning] {e}", file=sys.stderr)
            self.tray = None

    def update_tray_menu(self):
        if not self.tray:
            return
        try:
            menu = Gtk.Menu()

            # 1. Ablak megjelenítése / elrejtése
            is_vis = self.is_visible()
            toggle_label = "Ablak elrejtése" if is_vis else "Ablak megjelenítése"
            item_toggle = Gtk.MenuItem(label=toggle_label)
            item_toggle.connect("activate", lambda *_: self.toggle_window_visibility())
            menu.append(item_toggle)

            menu.append(Gtk.SeparatorMenuItem())

            # 2. Kezdőlap
            item_home = Gtk.MenuItem(label="🏠 Kezdőlap")
            item_home.connect("activate", lambda *_: (self.show_window_and_present(), self.switch_to_tab("home")))
            menu.append(item_home)

            # 3. Fülek gyorsválasztása
            tabs = self.config.get("tabs", [])
            if tabs:
                menu.append(Gtk.SeparatorMenuItem())
                active_id = self.config.get("activeTabId")
                for t in tabs:
                    t_id = t.get("id")
                    t_title = t.get("title") or t.get("name") or "Szolgáltatás"
                    unread = t.get("unreadCount", 0)
                    badge = f" ({unread})" if unread > 0 else ""
                    mark = "● " if t_id == active_id else "  "
                    item_tab = Gtk.MenuItem(label=f"{mark}{t_title}{badge}")
                    item_tab.connect("activate", lambda *_, tid=t_id: (self.show_window_and_present(), self.switch_to_tab(tid)))
                    menu.append(item_tab)

            menu.append(Gtk.SeparatorMenuItem())

            # 4. Végleges kilépés
            item_quit = Gtk.MenuItem(label="Végleges kilépés")
            item_quit.connect("activate", lambda *_: self.quit_application())
            menu.append(item_quit)

            menu.show_all()
            self.tray_menu = menu
            self.tray.set_menu(menu)
        except Exception as err:
            print(f"[Tray Menu Error] {err}", file=sys.stderr)

    def toggle_window_visibility(self):
        if self.is_visible():
            self.hide()
        else:
            self.show_window_and_present()
        self.update_tray_menu()

    def show_window_and_present(self):
        self.show_all()
        self.present()
        self._notify_active_webview_resize()
        self.update_tray_menu()

    def quit_application(self):
        Gtk.main_quit()

    def _apply_sidebar_width(self, collapsed: bool):
        width = SIDEBAR_COLLAPSED_WIDTH if collapsed else SIDEBAR_EXPANDED_WIDTH
        self._current_sidebar_width = width
        self.sidebar_box.set_size_request(width, -1)
        self.sidebar_webview.set_size_request(width, -1)
        if self.main_paned.get_position() != width:
            self.main_paned.set_position(width)
        GLib.timeout_add(60, self._notify_active_webview_resize)

    def _on_paned_position_changed(self, paned, param):
        expected = SIDEBAR_COLLAPSED_WIDTH if self.config.get("sidebarCollapsed") else SIDEBAR_EXPANDED_WIDTH
        if paned.get_position() != expected:
            paned.set_position(expected)

    def _notify_active_webview_resize(self):
        expected = SIDEBAR_COLLAPSED_WIDTH if self.config.get("sidebarCollapsed") else SIDEBAR_EXPANDED_WIDTH
        if self.main_paned.get_position() != expected:
            self.main_paned.set_position(expected)
        self.welcome_webview.run_javascript("window.dispatchEvent(new Event('resize'));", None, None, None)
        active_id = self.config.get("activeTabId")
        if active_id and active_id in self.tab_webviews:
            wv = self.tab_webviews[active_id]
            wv.run_javascript("window.dispatchEvent(new Event('resize'));", None, None, None)
        return False

    def on_window_state_event(self, widget, event):
        GLib.timeout_add(80, self._notify_active_webview_resize)
        return False

    def _on_sidebar_button_press(self, widget, event):
        if getattr(event, "button", None) == 3:
            try:
                self._last_button_event = event.copy()
            except Exception:
                self._last_button_event = event
        return False

    def setup_ui(self):
        initial_width = SIDEBAR_COLLAPSED_WIDTH if self.config.get("sidebarCollapsed") else SIDEBAR_EXPANDED_WIDTH
        self._current_sidebar_width = initial_width

        self.main_paned = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        self.main_paned.set_wide_handle(False)
        self.main_paned.set_hexpand(True)
        self.main_paned.set_vexpand(True)
        self.add(self.main_paned)

        # 1. BAL PANEL: Vertikális Fülsáv (sidebar.html)
        self.sidebar_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.sidebar_box.set_size_request(initial_width, -1)
        self.sidebar_box.set_hexpand(False)
        self.sidebar_box.set_vexpand(True)
        self.main_paned.pack1(self.sidebar_box, resize=False, shrink=True)

        self.sidebar_content_manager = WebKit2.UserContentManager()
        self.sidebar_content_manager.register_script_message_handler("tabbedclient")
        self.sidebar_content_manager.register_script_message_handler("tabbedClient")
        self.sidebar_content_manager.connect("script-message-received::tabbedclient", self.on_script_message)
        self.sidebar_content_manager.connect("script-message-received::tabbedClient", self.on_script_message)

        self.sidebar_webview = WebKit2.WebView.new_with_user_content_manager(self.sidebar_content_manager)
        self.sidebar_webview.set_size_request(initial_width, -1)
        self.sidebar_webview.set_hexpand(False)
        self.sidebar_webview.set_vexpand(True)
        self.sidebar_webview.set_background_color(Gdk.RGBA(0.086, 0.094, 0.114, 1.0))
        self.sidebar_webview.connect("button-press-event", self._on_sidebar_button_press)
        self.sidebar_webview.connect("context-menu", lambda *_: True)

        s_settings = self.sidebar_webview.get_settings()
        s_settings.set_enable_javascript(True)
        s_settings.set_allow_file_access_from_file_urls(True)
        s_settings.set_allow_universal_access_from_file_urls(True)
        s_settings.set_enable_write_console_messages_to_stdout(True)

        sidebar_url = GLib.filename_to_uri(os.path.join(SRC_DIR, "sidebar.html"), None)
        self.sidebar_webview.load_uri(sidebar_url)
        self.sidebar_webview.connect("load-changed", self.on_webview_load_changed)
        self.sidebar_box.pack_start(self.sidebar_webview, True, True, 0)

        # 2. JOBB PANEL: Kezdőlap és szolgáltatás WebView-k konténere
        self.content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.content_box.set_hexpand(True)
        self.content_box.set_vexpand(True)
        self.main_paned.pack2(self.content_box, resize=True, shrink=True)

        self.main_paned.set_position(initial_width)
        self.main_paned.connect("notify::position", self._on_paned_position_changed)

        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.NONE)
        self.stack.set_hexpand(True)
        self.stack.set_vexpand(True)
        self.content_box.pack_start(self.stack, True, True, 0)

        self.welcome_cm = WebKit2.UserContentManager()
        self.welcome_cm.register_script_message_handler("tabbedclient")
        self.welcome_cm.register_script_message_handler("tabbedClient")
        self.welcome_cm.connect("script-message-received::tabbedclient", self.on_script_message)
        self.welcome_cm.connect("script-message-received::tabbedClient", self.on_script_message)

        self.welcome_webview = WebKit2.WebView.new_with_user_content_manager(self.welcome_cm)
        self.welcome_webview.set_hexpand(True)
        self.welcome_webview.set_vexpand(True)
        self.welcome_webview.set_background_color(Gdk.RGBA(0.059, 0.067, 0.082, 1.0))
        self.welcome_webview.connect("context-menu", lambda *_: True)

        w_settings = self.welcome_webview.get_settings()
        w_settings.set_enable_javascript(True)
        w_settings.set_allow_file_access_from_file_urls(True)
        w_settings.set_allow_universal_access_from_file_urls(True)
        w_settings.set_enable_write_console_messages_to_stdout(True)

        welcome_url = GLib.filename_to_uri(os.path.join(SRC_DIR, "welcome.html"), None)
        self.welcome_webview.load_uri(welcome_url)
        self.welcome_webview.connect("load-changed", self.on_webview_load_changed)
        self.welcome_webview.add_events(Gdk.EventMask.SCROLL_MASK | Gdk.EventMask.SMOOTH_SCROLL_MASK)
        self.welcome_webview.connect("scroll-event", self._on_webview_scroll)
        self.welcome_webview.connect("decide-policy", self._on_welcome_decide_policy)

        self.stack.add_named(self.welcome_webview, "welcome")

        # Mentett fülek előtöltése induláskor
        saved_tabs = self.config.get("tabs", [])
        for tab in saved_tabs:
            self._ensure_tab_webview(tab)

        saved_active = self.config.get("activeTabId")
        if saved_active and saved_active in self.webviews:
            self.previous_tab_id = saved_active
            self.stack.set_visible_child_name(saved_active)
            active_tab = next((t for t in saved_tabs if t.get("id") == saved_active), None)
            if active_tab:
                title = active_tab.get("title") or active_tab.get("name") or "Szolgáltatás"
                self.set_title(f"{title} — TabbedClient")
        else:
            self.config["activeTabId"] = None
            self.stack.set_visible_child_name("welcome")

    def on_webview_load_changed(self, webview, load_event):
        if load_event == WebKit2.LoadEvent.FINISHED:
            self.sync_all_views()

    def on_window_delete(self, widget, event):
        settings = self.config.get("settings", {})
        minimize_tray = settings.get("minimizeToTrayOnClose", True)
        if minimize_tray and self.tray is not None:
            self.hide()
            self.update_tray_menu()
            return True
        self.quit_application()
        return False

    def get_profile_context(self, profile_id: str) -> WebKit2.WebContext:
        if not profile_id:
            profile_id = "default"
        if profile_id in self.contexts:
            return self.contexts[profile_id]

        profile_path = os.path.join(PROFILES_DIR, profile_id)
        base_cache = os.path.join(profile_path, "cache")
        base_data = os.path.join(profile_path, "data")
        favicon_dir = os.path.join(profile_path, "favicons")
        os.makedirs(base_cache, exist_ok=True)
        os.makedirs(base_data, exist_ok=True)
        os.makedirs(favicon_dir, exist_ok=True)

        data_manager = WebKit2.WebsiteDataManager(
            base_cache_directory=base_cache,
            base_data_directory=base_data
        )
        context = WebKit2.WebContext.new_with_website_data_manager(data_manager)
        if hasattr(WebKit2, "CacheModel"):
            context.set_cache_model(WebKit2.CacheModel.WEB_BROWSER)
        if hasattr(context, "set_favicon_database_directory"):
            context.set_favicon_database_directory(favicon_dir)

        cookie_manager = context.get_cookie_manager()
        cookie_file = os.path.join(profile_path, "cookies.sqlite")
        cookie_manager.set_persistent_storage(
            cookie_file,
            WebKit2.CookiePersistentStorage.SQLITE
        )
        cookie_manager.set_accept_policy(WebKit2.CookieAcceptPolicy.NO_THIRD_PARTY)

        self.contexts[profile_id] = context
        return context

    def _update_tab_favicon(self, tab_id: str, favicon_data: str = None, favicon_url: str = None):
        changed = False
        for t in self.config.get("tabs", []):
            if t.get("id") == tab_id:
                if favicon_data and t.get("favicon") != favicon_data:
                    t["favicon"] = favicon_data
                    changed = True
                if favicon_url and t.get("faviconUrl") != favicon_url:
                    t["faviconUrl"] = favicon_url
                    changed = True
                break
        if changed:
            save_config(self.config)
            self.sync_all_views()

    def _on_permission_request(self, webview, request, tab_id: str):
        # 1. Értesítési engedélykérés
        if hasattr(WebKit2, 'NotificationPermissionRequest') and isinstance(request, WebKit2.NotificationPermissionRequest):
            tab = next((t for t in self.config.get("tabs", []) if t.get("id") == tab_id), None)
            if tab and tab.get("notificationsEnabled", True) is False:
                request.deny()
            else:
                request.allow()
            return True

        # 2. Médiaeszközök (mikrofon / kamera): megerősítés kérése
        if hasattr(WebKit2, 'UserMediaPermissionRequest') and isinstance(request, WebKit2.UserMediaPermissionRequest):
            tab = next((t for t in self.config.get("tabs", []) if t.get("id") == tab_id), None)
            name = tab.get("title") or tab.get("name") or "A weboldal" if tab else "A weboldal"
            dialog = Gtk.MessageDialog(
                transient_for=self,
                flags=Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
                message_type=Gtk.MessageType.QUESTION,
                buttons=Gtk.ButtonsType.NONE,
                text=f"{name} hozzáférést kér a mikrofonhoz / kamerához."
            )
            dialog.format_secondary_text("Engedélyezed a médiaeszközök használatát ehhez a szolgáltatáshoz?")
            dialog.add_button("Tiltás", Gtk.ResponseType.NO)
            dialog.add_button("Engedélyezés", Gtk.ResponseType.YES)
            dialog.set_default_response(Gtk.ResponseType.NO)
            response = dialog.run()
            dialog.destroy()
            if response == Gtk.ResponseType.YES:
                request.allow()
            else:
                request.deny()
            return True

        # 3. Egyéb jogosultságok (pl. Geolocation): alapértelmezett védelem
        request.deny()
        return True

    def _on_show_notification(self, webview, notification, tab_id: str):
        tab = next((t for t in self.config.get("tabs", []) if t.get("id") == tab_id), None)
        if tab and tab.get("notificationsEnabled", True) is False:
            return True

        title = notification.get_title() or "Új értesítés"
        body = notification.get_body() or ""
        tab_name = tab.get("title") or tab.get("name") or "Szolgáltatás" if tab else "Szolgáltatás"

        is_active = (self.config.get("activeTabId") == tab_id and self.is_visible())
        if not is_active:
            if tab:
                tab["unreadCount"] = tab.get("unreadCount", 0) + 1
                save_config(self.config)
                self.sync_all_views()
            if Notify and Notify.is_initted():
                try:
                    notif = Notify.Notification.new(f"[{tab_name}] {title}", body, "dialog-information")
                    notif.show()
                except Exception as err:
                    print(f"[Notify Error] {err}", file=sys.stderr)
        return True

    def _on_tab_title_changed(self, webview, param, tab_id: str):
        new_title = webview.get_title() or ""
        tab = next((t for t in self.config.get("tabs", []) if t.get("id") == tab_id), None)
        if not tab:
            return

        # Olvasatlan számláló kinyerése a címből (pl. '(3) Gmail' vagy '[2] Slack')
        m = re.search(r'[\(\[]([0-9]+)\+?[\)\]]', new_title)
        if m:
            count = int(m.group(1))
            if tab.get("unreadCount") != count:
                tab["unreadCount"] = count
                save_config(self.config)
                self.sync_all_views()
        elif self.config.get("activeTabId") == tab_id:
            if tab.get("unreadCount", 0) > 0:
                tab["unreadCount"] = 0
                save_config(self.config)
                self.sync_all_views()

    def open_external_uri(self, uri: str):
        if not uri:
            return
        real_uri = extract_real_target_url(uri)
        if not real_uri or real_uri.startswith("about:") or real_uri.startswith("javascript:"):
            return

        print(f"[TabbedClient] Külső link megnyitása alapértelmezett böngészőben: {real_uri}")

        # 1. GIO AppInfo (modern Freedesktop / GNOME / Zorin OS szabvány)
        try:
            if hasattr(Gio.AppInfo, "launch_default_for_uri"):
                if Gio.AppInfo.launch_default_for_uri(real_uri, None):
                    return
        except Exception as e:
            print(f"[Open External URI Gio Warning] {e}", file=sys.stderr)

        # 2. Közvetlen xdg-open parancs (Linux asztali környezetek)
        try:
            subprocess.Popen(["xdg-open", real_uri], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return
        except Exception:
            pass

        # 3. Python webbrowser modul (minden platform)
        try:
            import webbrowser
            if webbrowser.open(real_uri):
                return
        except Exception as e:
            print(f"[Open External URI Webbrowser Warning] {e}", file=sys.stderr)

        # 4. Gtk.show_uri fallback
        try:
            time = Gtk.get_current_event_time() or Gdk.CURRENT_TIME
            if hasattr(Gtk, "show_uri_on_window") and self.get_window():
                Gtk.show_uri_on_window(self, real_uri, time)
                return
            elif hasattr(Gtk, "show_uri") and hasattr(self, "get_screen") and self.get_screen():
                Gtk.show_uri(self.get_screen(), real_uri, time)
                return
        except Exception:
            pass

    def _on_welcome_decide_policy(self, webview, decision, decision_type):
        if decision_type in (WebKit2.PolicyDecisionType.NAVIGATION_ACTION, WebKit2.PolicyDecisionType.NEW_WINDOW_ACTION):
            nav_action = decision.get_navigation_action()
            req = nav_action.get_request() if nav_action else None
            uri = req.get_uri() if req else None
            if uri and (uri.startswith("http://") or uri.startswith("https://")):
                self.open_external_uri(uri)
                decision.ignore()
                return True
        return False

    def _on_create_webview(self, webview, navigation_action, tab_id: str):
        """Kezeli a target='_blank' vagy window.open() hívásokat."""
        is_gesture = navigation_action.is_user_gesture() if navigation_action else False
        req = navigation_action.get_request() if navigation_action else None
        uri = req.get_uri() if req else None

        # Ha nem felhasználói gesztus indította (pl. háttérben futó script, automata popup vagy Meta MAW proxy)
        if not is_gesture:
            return None

        tab = next((t for t in self.config.get("tabs", []) if t.get("id") == tab_id), None)
        tab_url = tab.get("url", "") if tab else (webview.get_uri() or "")

        if uri and not uri.startswith("about:") and not uri.startswith("javascript:"):
            real_url = extract_real_target_url(uri)
            if is_auth_or_login_url(real_url):
                # OAuth / azonosítási folyamat a fülön belül folytatódik
                webview.load_uri(real_url)
                return None
            elif is_external_link(tab_url, real_url):
                self.open_external_uri(real_url)
                return None
            else:
                webview.load_uri(real_url)
                return None

        # Ha az URI a létrehozás pillanatában még nem ismert, de van felhasználói gesztus
        try:
            temp_wv = WebKit2.WebView.new_with_context(webview.get_context())

            def _on_temp_decide_policy(temp_view, decision, decision_type):
                if decision_type == WebKit2.PolicyDecisionType.NAVIGATION_ACTION:
                    na = decision.get_navigation_action()
                    r = na.get_request() if na else None
                    u = r.get_uri() if r else None
                    if u and not u.startswith("about:") and not u.startswith("javascript:"):
                        real_u = extract_real_target_url(u)
                        if is_auth_or_login_url(real_u):
                            webview.load_uri(real_u)
                        else:
                            curr_tab = next((t for t in self.config.get("tabs", []) if t.get("id") == tab_id), None)
                            curr_tab_url = curr_tab.get("url", "") if curr_tab else (webview.get_uri() or "")
                            if is_external_link(curr_tab_url, real_u):
                                self.open_external_uri(real_u)
                            else:
                                webview.load_uri(real_u)
                decision.ignore()
                GLib.idle_add(temp_view.destroy)
                return True

            temp_wv.connect("decide-policy", _on_temp_decide_policy)
            GLib.timeout_add(10000, temp_wv.destroy)
            return temp_wv
        except Exception as err:
            print(f"[Create WebView Warning] {err}", file=sys.stderr)
            return None

    def _on_decide_policy(self, webview, decision, decision_type, tab_id: str):
        """Kezeli a navigációs döntéseket (új ablak, link kattintás, külső domain)."""
        tab = next((t for t in self.config.get("tabs", []) if t.get("id") == tab_id), None)
        tab_url = tab.get("url", "") if tab else (webview.get_uri() or "")

        # 1. Új ablak művelet (pl. link target='_blank' vagy window.open)
        if decision_type == WebKit2.PolicyDecisionType.NEW_WINDOW_ACTION:
            nav_action = decision.get_navigation_action()
            is_gesture = nav_action.is_user_gesture() if nav_action else False
            req = nav_action.get_request() if nav_action else None
            uri = req.get_uri() if req else None
            if uri and not uri.startswith("about:") and not uri.startswith("javascript:"):
                real_url = extract_real_target_url(uri)
                if is_auth_or_login_url(real_url):
                    webview.load_uri(real_url)
                elif is_gesture:
                    if is_external_link(tab_url, real_url):
                        self.open_external_uri(real_url)
                    else:
                        webview.load_uri(real_url)
            decision.ignore()
            return True

        # 2. Bármilyen navigációs művelet (LINK_CLICKED, OTHER, REDIRECT, stb.)
        if decision_type == WebKit2.PolicyDecisionType.NAVIGATION_ACTION:
            nav_action = decision.get_navigation_action()
            if not nav_action:
                return False

            mouse_btn = nav_action.get_mouse_button()
            modifiers = nav_action.get_modifiers()
            ctrl_pressed = bool(modifiers & Gdk.ModifierType.CONTROL_MASK)
            nav_type = nav_action.get_navigation_type()
            is_gesture = nav_action.is_user_gesture()

            req = nav_action.get_request()
            uri = req.get_uri() if req else None
            if not uri or uri.startswith("about:") or uri.startswith("javascript:"):
                return False

            # Középső egérgomb vagy Ctrl + bal klikk mindig külső böngészőben nyílik
            if mouse_btn == 2 or ctrl_pressed:
                self.open_external_uri(uri)
                decision.ignore()
                return True

            # Csak akkor nyitunk külső böngészőt, ha kifejezett felhasználói kattintás történt!
            # Háttérben futó scriptek, automatikus átirányítások, iframe-ek (user_gesture nélkül) a WebView-n belül maradnak.
            is_user_click = (nav_type == WebKit2.NavigationType.LINK_CLICKED) or (is_gesture and mouse_btn in (1, 2))
            if is_user_click:
                if is_external_link(tab_url, uri):
                    self.open_external_uri(uri)
                    decision.ignore()
                    return True

        return False

    def _on_webview_scroll(self, webview, event):
        """Kezeli a Ctrl + egérgörgő nagyítást és kicsinyítést (Zoom In / Zoom Out)."""
        if bool(event.state & Gdk.ModifierType.CONTROL_MASK):
            current_zoom = webview.get_zoom_level()
            new_zoom = current_zoom

            if event.direction == Gdk.ScrollDirection.UP:
                new_zoom = min(5.0, current_zoom + 0.1)
            elif event.direction == Gdk.ScrollDirection.DOWN:
                new_zoom = max(0.25, current_zoom - 0.1)
            elif event.direction == Gdk.ScrollDirection.SMOOTH:
                has_deltas, dx, dy = event.get_scroll_deltas()
                if has_deltas:
                    if dy < 0:
                        new_zoom = min(5.0, current_zoom + 0.1)
                    elif dy > 0:
                        new_zoom = max(0.25, current_zoom - 0.1)

            if abs(new_zoom - current_zoom) > 0.001:
                webview.set_zoom_level(round(new_zoom, 2))
            return True

        return False

    def _on_window_key_press(self, widget, event):
        """Kezeli a billentyűzet-alapú nagyítást: Ctrl+, Ctrl-, Ctrl0."""
        if bool(event.state & Gdk.ModifierType.CONTROL_MASK):
            keyval = event.keyval
            if keyval in (Gdk.KEY_plus, Gdk.KEY_equal, Gdk.KEY_KP_Add):
                self._zoom_active_view(0.1)
                return True
            elif keyval in (Gdk.KEY_minus, Gdk.KEY_KP_Subtract):
                self._zoom_active_view(-0.1)
                return True
            elif keyval in (Gdk.KEY_0, Gdk.KEY_KP_0):
                self._reset_active_zoom()
                return True
        return False

    def _get_active_or_visible_webview(self):
        active_id = self.config.get("activeTabId")
        if active_id and active_id in self.webviews:
            return self.webviews[active_id]
        if hasattr(self, "welcome_webview") and self.stack.get_visible_child_name() == "welcome":
            return self.welcome_webview
        return None

    def _zoom_active_view(self, delta: float):
        wv = self._get_active_or_visible_webview()
        if wv:
            cur = wv.get_zoom_level()
            target = max(0.25, min(5.0, round(cur + delta, 2)))
            wv.set_zoom_level(target)

    def _reset_active_zoom(self):
        wv = self._get_active_or_visible_webview()
        if wv:
            wv.set_zoom_level(1.0)

    def _ensure_tab_webview(self, tab: dict):
        tab_id = tab.get("id")
        if not tab_id or tab_id in self.webviews:
            return
        profile = tab.get("profile") or tab.get("profileId") or "default"
        url = tab.get("url", "https://example.com")

        ctx = self.get_profile_context(profile)

        wv_settings = WebKit2.Settings()
        wv_settings.set_enable_javascript(True)
        wv_settings.set_enable_webaudio(True)
        wv_settings.set_enable_media_stream(True)
        wv_settings.set_enable_smooth_scrolling(True)
        wv_settings.set_javascript_can_access_clipboard(True)
        if hasattr(wv_settings, "set_zoom_text_only"):
            wv_settings.set_zoom_text_only(False)
        if hasattr(wv_settings, "set_enable_page_cache"):
            wv_settings.set_enable_page_cache(True)
        if hasattr(wv_settings, "set_enable_dns_prefetching"):
            wv_settings.set_enable_dns_prefetching(True)
        wv_settings.set_user_agent(
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
        )

        wv = WebKit2.WebView.new_with_context(ctx)
        wv.set_settings(wv_settings)
        wv.set_hexpand(True)
        wv.set_vexpand(True)
        wv.set_background_color(Gdk.RGBA(0.059, 0.067, 0.082, 1.0))

        # Nagyítás és kicsinyítés kezelése (Ctrl + egérgörgő)
        wv.add_events(Gdk.EventMask.SCROLL_MASK | Gdk.EventMask.SMOOTH_SCROLL_MASK)
        wv.connect("scroll-event", self._on_webview_scroll)

        # Biztonságos jogosultságkezelés és értesítési híd
        wv.connect("permission-request", lambda w, r: self._on_permission_request(w, r, tab_id))
        wv.connect("show-notification", lambda w, n: self._on_show_notification(w, n, tab_id))
        wv.connect("notify::title", lambda w, p: self._on_tab_title_changed(w, p, tab_id))

        # Külső hivatkozások megnyitása külső böngészőben (pl. Gmail 'View in browser', e-mail linkek)
        wv.connect("decide-policy", lambda w, d, dt: self._on_decide_policy(w, d, dt, tab_id))
        wv.connect("create", lambda w, a: self._on_create_webview(w, a, tab_id))

        container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        container.set_hexpand(True)
        container.set_vexpand(True)

        progress_bar = Gtk.ProgressBar()
        progress_bar.set_hexpand(True)
        progress_bar.set_fraction(0.15)
        progress_bar.set_no_show_all(True)
        progress_bar.show()

        def on_favicon_changed(view, param):
            try:
                surface = view.get_favicon()
                if surface is not None:
                    buf = io.BytesIO()
                    surface.write_to_png(buf)
                    b64 = base64.b64encode(buf.getvalue()).decode("ascii")
                    if b64:
                        self._update_tab_favicon(tab_id, favicon_data=f"data:image/png;base64,{b64}")
            except Exception:
                pass

        def on_dom_favicon_extracted(view, res, user_data):
            try:
                js_res = view.run_javascript_finish(res)
                val = js_res.get_js_value()
                if val and val.is_string():
                    href = val.to_string().strip()
                    if href.startswith("http://") or href.startswith("https://") or href.startswith("data:image/"):
                        self._update_tab_favicon(tab_id, favicon_url=href)
            except Exception:
                pass

        def on_tab_load_changed(view, event):
            if event == WebKit2.LoadEvent.STARTED:
                progress_bar.set_fraction(0.15)
                progress_bar.show()
            elif event == WebKit2.LoadEvent.COMMITTED:
                progress_bar.set_fraction(max(0.4, view.get_estimated_load_progress()))
            elif event == WebKit2.LoadEvent.FINISHED:
                progress_bar.hide()
                js_extract = (
                    "(function(){"
                    "var el=document.querySelector('link[rel*=\"icon\"]');"
                    "return (el&&el.href)?el.href:(location.origin+'/favicon.ico');"
                    "})();"
                )
                view.run_javascript(js_extract, None, on_dom_favicon_extracted, None)

        def on_tab_progress(view, param):
            p = view.get_estimated_load_progress()
            if 0.0 < p < 1.0:
                progress_bar.set_fraction(max(0.1, p))
                progress_bar.show()
            elif p >= 1.0:
                progress_bar.hide()

        wv.connect("notify::favicon", on_favicon_changed)
        wv.connect("load-changed", on_tab_load_changed)
        wv.connect("notify::estimated-load-progress", on_tab_progress)

        container.pack_start(progress_bar, False, False, 0)
        container.pack_start(wv, True, True, 0)

        self.webviews[tab_id] = container
        self.tab_webviews[tab_id] = wv
        self.stack.add_named(container, tab_id)
        container.show_all()
        progress_bar.show()
        wv.load_uri(url)

    def _create_icon_menu_item(self, icon_name: str, label_text: str) -> Gtk.MenuItem:
        item = Gtk.MenuItem()
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        icon = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.MENU)
        label = Gtk.Label(label=label_text, xalign=0.0)
        box.pack_start(icon, False, False, 0)
        box.pack_start(label, True, True, 0)
        item.add(box)
        return item

    def reload_tab(self, tab_id: str):
        if not tab_id or tab_id == "home":
            tab_id = self.config.get("activeTabId")
        if not tab_id or tab_id == "home":
            return
        if self.config.get("activeTabId") != tab_id:
            self.switch_to_tab(tab_id)
        wv = self.tab_webviews.get(tab_id)
        if wv is not None:
            wv.reload()

    def toggle_tab_notifications(self, tab_id: str):
        tabs = self.config.get("tabs", [])
        tab = next((t for t in tabs if t.get("id") == tab_id), None)
        if tab:
            tab["notificationsEnabled"] = not tab.get("notificationsEnabled", True)
            save_config(self.config)
            self.sync_all_views()

    def move_tab(self, tab_id: str, direction: int):
        tabs = self.config.get("tabs", [])
        idx = next((i for i, t in enumerate(tabs) if t.get("id") == tab_id), -1)
        if idx == -1:
            return
        new_idx = idx + direction
        if 0 <= new_idx < len(tabs):
            tabs[idx], tabs[new_idx] = tabs[new_idx], tabs[idx]
            for i, t in enumerate(tabs):
                t["order"] = i
            save_config(self.config)
            self.sync_all_views()

    def show_sidebar_context_menu(self, tab_id: str):
        target_service_id = tab_id if (tab_id and tab_id != "home") else self.config.get("activeTabId")
        has_service = bool(
            target_service_id
            and any(t.get("id") == target_service_id for t in self.config.get("tabs", []))
        )
        target_tab = next((t for t in self.config.get("tabs", []) if t.get("id") == target_service_id), None) if has_service else None

        menu = Gtk.Menu()
        self._context_menu = menu

        item_home = self._create_icon_menu_item("go-home-symbolic", "Kezdőlap")
        item_home.connect("activate", lambda *_: self.switch_to_tab("home"))
        menu.append(item_home)

        item_reload = self._create_icon_menu_item("view-refresh-symbolic", "Frissítés")
        item_reload.set_sensitive(has_service)
        item_reload.connect("activate", lambda *_: self.reload_tab(target_service_id))
        menu.append(item_reload)

        if has_service and target_tab:
            # Értesítések némítása / feloldása
            is_muted = not target_tab.get("notificationsEnabled", True)
            mute_icon = "audio-volume-high-symbolic" if is_muted else "audio-volume-muted-symbolic"
            mute_text = "Értesítések engedélyezése" if is_muted else "Értesítések némítása"
            item_mute = self._create_icon_menu_item(mute_icon, mute_text)
            item_mute.connect("activate", lambda *_: self.toggle_tab_notifications(target_service_id))
            menu.append(item_mute)

            # Mozgatás fel / le
            tabs = self.config.get("tabs", [])
            idx = next((i for i, t in enumerate(tabs) if t.get("id") == target_service_id), -1)

            item_up = self._create_icon_menu_item("go-up-symbolic", "Mozgatás feljebb")
            item_up.set_sensitive(idx > 0)
            item_up.connect("activate", lambda *_: self.move_tab(target_service_id, -1))
            menu.append(item_up)

            item_down = self._create_icon_menu_item("go-down-symbolic", "Mozgatás lejjebb")
            item_down.set_sensitive(idx >= 0 and idx < len(tabs) - 1)
            item_down.connect("activate", lambda *_: self.move_tab(target_service_id, 1))
            menu.append(item_down)

        menu.append(Gtk.SeparatorMenuItem())

        item_delete = self._create_icon_menu_item("user-trash-symbolic", "Szolgáltatás törlése")
        item_delete.set_sensitive(has_service)
        item_delete.connect("activate", lambda *_: self._delete_tab_by_id(target_service_id))
        menu.append(item_delete)

        menu.show_all()
        if self._last_button_event is not None:
            menu.popup_at_pointer(self._last_button_event)
        else:
            menu.popup(None, None, None, None, 3, Gtk.get_current_event_time())

    def _delete_tab_by_id(self, tab_id: str):
        if not tab_id:
            return
        target_tab = next((t for t in self.config.get("tabs", []) if t.get("id") == tab_id), None)
        if not target_tab:
            return

        title = target_tab.get("title") or target_tab.get("name") or "Szolgáltatás"
        url = target_tab.get("url", "")

        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.NONE,
            text=f"Biztosan törölni szeretnéd a(z) „{title}” szolgáltatást?"
        )
        dialog.format_secondary_text(
            f"Webcím: {url}\nA szolgáltatás fül eltávolításra kerül a listából."
        )
        dialog.add_button("Mégse", Gtk.ResponseType.CANCEL)
        del_btn = dialog.add_button("Törlés", Gtk.ResponseType.OK)
        try:
            del_btn.get_style_context().add_class("destructive-action")
        except Exception:
            pass
        dialog.set_default_response(Gtk.ResponseType.CANCEL)

        response = dialog.run()
        dialog.destroy()
        if response != Gtk.ResponseType.OK:
            return

        self.config["tabs"] = [t for t in self.config["tabs"] if t["id"] != tab_id]
        self.tab_webviews.pop(tab_id, None)
        if tab_id in self.webviews:
            widget = self.webviews.pop(tab_id)
            self.stack.remove(widget)
            widget.destroy()

        if self.previous_tab_id == tab_id:
            self.previous_tab_id = None

        if self.config.get("activeTabId") == tab_id:
            remaining = self.config["tabs"]
            if remaining:
                self.switch_to_tab(remaining[0]["id"])
            else:
                self.switch_to_tab("home")
        else:
            save_config(self.config)
            self.sync_all_views()

    def sync_all_views(self):
        collapsed = bool(self.config.get("sidebarCollapsed", False))
        self._apply_sidebar_width(collapsed)

        normalized_tabs = []
        for idx, t in enumerate(self.config.get("tabs", [])):
            title = t.get("title") or t.get("name") or "Szolgáltatás"
            profile = t.get("profile") or t.get("profileId") or "default"
            url = t.get("url", "https://example.com")
            notifications_enabled = bool(t.get("notificationsEnabled", True))
            unread_count = int(t.get("unreadCount", 0))
            order = int(t.get("order", idx))
            normalized_tabs.append({
                "id": t.get("id"),
                "title": title,
                "name": title,
                "url": url,
                "icon": t.get("icon") or "globe",
                "profile": profile,
                "profileId": profile,
                "notificationsEnabled": notifications_enabled,
                "unreadCount": unread_count,
                "order": order,
                "favicon": t.get("favicon") or "",
                "faviconUrl": t.get("faviconUrl") or _default_favicon_url(url)
            })
        self.config["tabs"] = normalized_tabs

        settings = self.config.get("settings", {})
        payload = {
            "version": self.config.get("version", "1.0.0"),
            "theme": self.config.get("theme", "slate"),
            "sidebarCollapsed": collapsed,
            "activeTabId": self.config.get("activeTabId") or "home",
            "tabs": normalized_tabs,
            "profiles": self.config.get("profiles", []),
            "view": self.current_welcome_view,
            "settings": {
                "theme": self.config.get("theme", "slate"),
                "sidebarCollapsed": collapsed,
                "minimizeToTrayOnClose": settings.get("minimizeToTrayOnClose", True),
                "startMinimized": settings.get("startMinimized", False),
                "hardwareAcceleration": settings.get("hardwareAcceleration", True)
            }
        }
        js_arg = json.dumps(payload, ensure_ascii=False)
        self.sidebar_webview.run_javascript(f"if (window.syncFromBackend) window.syncFromBackend({js_arg});", None, None, None)
        self.welcome_webview.run_javascript(f"if (window.syncFromBackend) window.syncFromBackend({js_arg});", None, None, None)
        self.update_tray_menu()

    def switch_to_tab(self, tab_id: str):
        if not tab_id or tab_id == "home":
            self.config["activeTabId"] = None
            self.current_welcome_view = "dashboard"
            save_config(self.config)
            self.stack.set_visible_child_name("welcome")
            self.set_title("TabbedClient — Kezdőlap")
            self.sync_all_views()
            return

        target_tab = next((t for t in self.config["tabs"] if t["id"] == tab_id), None)
        if not target_tab:
            return

        # Fülre váltáskor az olvasatlan számláló nullázása
        if target_tab.get("unreadCount", 0) > 0:
            target_tab["unreadCount"] = 0

        self._ensure_tab_webview(target_tab)
        self.config["activeTabId"] = tab_id
        self.previous_tab_id = tab_id
        save_config(self.config)

        self.stack.set_visible_child_name(tab_id)
        self.stack.show_all()
        title = target_tab.get("title") or target_tab.get("name") or "Szolgáltatás"
        self.set_title(f"{title} — TabbedClient")
        self.sync_all_views()

    def show_welcome_modal(self, view_name: str):
        current_active = self.config.get("activeTabId")
        if current_active and current_active != "home":
            self.previous_tab_id = current_active
        self.current_welcome_view = view_name
        self.config["activeTabId"] = None
        self.stack.set_visible_child_name("welcome")
        self.stack.show_all()
        if view_name == "settings":
            self.set_title("Beállítások — TabbedClient")
        elif view_name == "add-tab":
            self.set_title("Új szolgáltatás felvétele — TabbedClient")
        else:
            self.set_title("TabbedClient — Kezdőlap")
        self.sync_all_views()

    def cancel_welcome_modal(self):
        tabs = self.config.get("tabs", [])
        if self.previous_tab_id and any(t["id"] == self.previous_tab_id for t in tabs):
            target = self.previous_tab_id
            self.previous_tab_id = None
            self.switch_to_tab(target)
        else:
            self.switch_to_tab("home")

    def parse_js_message(self, js_result):
        val = js_result.get_js_value()
        if val.is_string():
            raw = val.to_string()
        else:
            raw = val.to_json(0)
        return json.loads(raw)

    def on_script_message(self, content_manager, js_result):
        try:
            msg = self.parse_js_message(js_result)
        except Exception as e:
            print(f"[IPC Error] {e}", file=sys.stderr)
            return

        msg_type = msg.get("type")

        if msg_type in ("SIDEBAR_READY", "WELCOME_READY"):
            self.sync_all_views()

        elif msg_type == "SET_COLLAPSED":
            collapsed = bool(msg.get("collapsed", False))
            self.config["sidebarCollapsed"] = collapsed
            self.config.setdefault("settings", {})["sidebarCollapsed"] = collapsed
            save_config(self.config)
            self._apply_sidebar_width(collapsed)
            self.sync_all_views()

        elif msg_type == "SET_THEME":
            theme = msg.get("theme", "slate")
            if theme in VALID_THEMES:
                self.config["theme"] = theme
                self.config.setdefault("settings", {})["theme"] = theme
                save_config(self.config)
                self.sync_all_views()

        elif msg_type == "SET_SETTINGS":
            settings = msg.get("settings", {})
            if isinstance(settings, dict):
                self.config.setdefault("settings", {}).update(settings)
                if "theme" in settings and settings["theme"] in VALID_THEMES:
                    self.config["theme"] = settings["theme"]
                if "sidebarCollapsed" in settings:
                    self.config["sidebarCollapsed"] = bool(settings["sidebarCollapsed"])
                save_config(self.config)
                self.sync_all_views()

        elif msg_type == "OPEN_ADD_TAB":
            self.show_welcome_modal("add-tab")

        elif msg_type == "OPEN_SETTINGS":
            self.show_welcome_modal("settings")

        elif msg_type == "CANCEL_MODAL":
            self.cancel_welcome_modal()

        elif msg_type == "SWITCH_TAB":
            tab_id = msg.get("id") or msg.get("tabId")
            self.switch_to_tab(tab_id)

        elif msg_type == "RELOAD_TAB":
            tab_id = msg.get("id") or msg.get("tabId")
            self.reload_tab(tab_id)

        elif msg_type == "SHOW_CONTEXT_MENU":
            tab_id = msg.get("id") or msg.get("tabId")
            self.show_sidebar_context_menu(tab_id)

        elif msg_type == "TOGGLE_MUTE":
            tab_id = msg.get("id") or msg.get("tabId")
            self.toggle_tab_notifications(tab_id)

        elif msg_type == "MOVE_TAB":
            tab_id = msg.get("id") or msg.get("tabId")
            direction = int(msg.get("direction", 0))
            if direction != 0:
                self.move_tab(tab_id, direction)

        elif msg_type == "ADD_TAB":
            tab_obj = msg.get("tab") if isinstance(msg.get("tab"), dict) else msg
            title = (tab_obj.get("title") or tab_obj.get("name") or "Új szolgáltatás").strip()
            profile = tab_obj.get("profile") or tab_obj.get("profileId") or "work"
            url = (tab_obj.get("url") or "https://example.com").strip()
            icon = tab_obj.get("icon") or "globe"
            new_tab = {
                "id": f"tab-{uuid.uuid4().hex[:8]}",
                "title": title,
                "name": title,
                "url": url,
                "icon": icon,
                "profile": profile,
                "profileId": profile,
                "notificationsEnabled": True,
                "unreadCount": 0,
                "order": len(self.config.get("tabs", [])),
                "favicon": "",
                "faviconUrl": _default_favicon_url(url)
            }
            self.config.setdefault("tabs", []).append(new_tab)
            save_config(self.config)
            self.switch_to_tab(new_tab["id"])

        elif msg_type == "DELETE_TAB":
            tab_id = msg.get("id") or msg.get("tabId")
            self._delete_tab_by_id(tab_id)


def main():
    win = TabbedClientWindow()
    Gtk.main()


if __name__ == "__main__":
    main()
