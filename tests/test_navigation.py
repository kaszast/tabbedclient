#!/usr/bin/env python3
"""
Egységtesztek a tabbedclient navigációs, URL-kibontási és külső/belső link döntéseihez.
Különös tekintettel a Meta MAW proxy (fbsbx.com), OAuth és külső böngésző nyitási logikára.
"""

import sys
import unittest

# Importáljuk a tabbedclient modulból a navigációs segédfüggvényeket
from desktop.tabbedclient import (
    extract_real_target_url,
    is_auth_or_login_url,
    is_external_link,
    are_domains_same_service,
    get_root_domain,
)


class TestNavigationLogic(unittest.TestCase):

    def test_get_root_domain(self):
        self.assertEqual(get_root_domain("www.messenger.com"), "messenger.com")
        self.assertEqual(get_root_domain("messenger.com"), "messenger.com")
        self.assertEqual(get_root_domain("mail.google.com"), "google.com")
        self.assertEqual(get_root_domain("google.co.uk"), "google.co.uk")
        self.assertEqual(get_root_domain("sub.domain.google.co.uk"), "google.co.uk")
        self.assertEqual(get_root_domain("www.fbsbx.com"), "fbsbx.com")

    def test_are_domains_same_service(self):
        # Meta csoport
        self.assertTrue(are_domains_same_service("www.messenger.com", "www.fbsbx.com"))
        self.assertTrue(are_domains_same_service("messenger.com", "facebook.com"))
        self.assertTrue(are_domains_same_service("web.whatsapp.com", "fbsbx.com"))
        self.assertTrue(are_domains_same_service("facebook.com", "fbcdn.net"))

        # Google csoport
        self.assertTrue(are_domains_same_service("mail.google.com", "accounts.google.com"))
        self.assertTrue(are_domains_same_service("mail.google.com", "calendar.google.com"))
        self.assertTrue(are_domains_same_service("mail.google.com", "gstatic.com"))

        # Microsoft csoport
        self.assertTrue(are_domains_same_service("outlook.live.com", "login.microsoftonline.com"))
        self.assertTrue(are_domains_same_service("teams.microsoft.com", "sharepoint.com"))

        # Nem azonos szolgáltatások
        self.assertFalse(are_domains_same_service("mail.google.com", "index.hu"))
        self.assertFalse(are_domains_same_service("messenger.com", "google.com"))
        self.assertFalse(are_domains_same_service("facebook.com", "malicious-site.com"))

    def test_is_auth_or_login_url(self):
        # Meta MAW proxy url (a hiba közvetlen kiváltója!)
        maw_url = (
            "https://www.fbsbx.com/maw_proxy_page/?__cci=FQARESIVAhn1nQEC5ALSAvoCJC6KAz5ARkhKTE5QVFhcXmBiZGhqbHJ0eHq"
        )
        self.assertTrue(is_auth_or_login_url(maw_url))

        # Általános auth / OAuth URL-ek
        self.assertTrue(is_auth_or_login_url("https://accounts.google.com/signin/v2/identifier"))
        self.assertTrue(is_auth_or_login_url("https://login.microsoftonline.com/common/oauth2/authorize"))
        self.assertTrue(is_auth_or_login_url("https://auth.slack.com/oauth/authorize"))
        self.assertTrue(is_auth_or_login_url("https://example.com/oauth/authorize"))
        self.assertTrue(is_auth_or_login_url("https://example.com/session/login"))

        # Hétköznapi linkek NEM auth URL-ek
        self.assertFalse(is_auth_or_login_url("https://index.hu/belfold"))
        self.assertFalse(is_auth_or_login_url("https://github.com/torvalds/linux"))

    def test_maw_proxy_is_not_external_link(self):
        # A felhasználó által jelzett eset: Messenger fül nyitva van, betöltődik a maw_proxy_page
        tab_url = "https://www.messenger.com/"
        maw_url = (
            "https://www.fbsbx.com/maw_proxy_page/?__cci=FQARESIVAhn1nQEC5ALSAvoCJC6KAz5ARkhKTE5QVFhcXmBiZGhqbHJ0eHq"
        )
        self.assertFalse(
            is_external_link(tab_url, maw_url),
            "A Meta maw_proxy_page-et belső kérésként kell kezelni, SOHA nem szabad külső böngészőben megnyitni!"
        )

    def test_is_external_link_real_links(self):
        gmail_tab = "https://mail.google.com/mail/u/0/#inbox"

        # Valódi külső linkek
        self.assertTrue(is_external_link(gmail_tab, "https://telex.hu/gazdasag"))
        self.assertTrue(is_external_link(gmail_tab, "https://github.com/trending"))

        # Belső Google linkek
        self.assertFalse(is_external_link(gmail_tab, "https://calendar.google.com/calendar"))
        self.assertFalse(is_external_link(gmail_tab, "https://drive.google.com/drive/my-drive"))
        self.assertFalse(is_external_link(gmail_tab, "https://accounts.google.com/ServiceLogin"))

        # Átirányított Google link (pl. Gmail levélben lévő link: /url?q=https://example.com)
        redirect_url = "https://www.google.com/url?q=https%3A%2F%2Fexample.com%2Fnews&sa=D&sntz=1&usg=AOvVaw0"
        self.assertTrue(
            is_external_link(gmail_tab, redirect_url),
            "A Google /url?q= átirányítás kibontás után külső linknek minősül!"
        )

        # Messenger átirányított link (pl. l.messenger.com/l.php?u=https://example.com)
        messenger_tab = "https://www.messenger.com/"
        fb_redirect = "https://l.messenger.com/l.php?u=https%3A%2F%2Fexample.org%2Farticle&h=AT1..."
        self.assertTrue(
            is_external_link(messenger_tab, fb_redirect),
            "A Messenger l.php átirányítás kibontás után külső linknek minősül!"
        )


if __name__ == "__main__":
    unittest.main()
