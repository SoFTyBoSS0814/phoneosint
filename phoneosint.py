#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import requests
import sys
import time
import random
import hashlib
from playwright.sync_api import sync_playwright

# Valós böngésző User-Agent stringek
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:123.0) Gecko/20100101 Firefox/123.0"
]

def get_random_headers():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept-Language": "hu-HU,hu;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
    }

# ==============================================================================
# MODULOK (SZOLGÁLTATÁSOK)
# ==============================================================================

def check_twitter(email):
    """
    Twitter/X ellenőrzési modul vázlat.
    """
    url = "https://api.twitter.com/i/users/email_available.json"
    params = {"email": email}
    
    try:
        response = requests.get(url, params=params, headers=get_random_headers(), timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("taken") == True or data.get("valid") == False:
                return "[+] Twitter/X: Az e-mail címhez tartozik regisztrált fiók."
    except requests.exceptions.RequestException:
        pass
    return None


def check_instagram(email):
    """
    Instagram ellenőrzés Playwright (Chromium) segítségével, 
    látható böngészőablakkal és lelassított lépésekkel.
    """
    try:
        with sync_playwright() as p:
            # headless=False -> Látható lesz a böngészőablak
            browser = p.chromium.launch(headless=False)
            page = browser.new_page(user_agent=random.choice(USER_AGENTS))
            
            # Megnyitjuk az Instagram regisztrációs oldalát
            page.goto("https://www.instagram.com/accounts/emailsignup/", timeout=15000)
            time.sleep(3)  # Várakozás, hogy betöltődjön az oldal
            
            # Adatok kitöltése jól látható ütemezéssel
            page.fill("input[name='email']", email)
            time.sleep(1.5)
            
            page.fill("input[name='fullName']", "OSINT Test")
            time.sleep(1.5)
            
            page.fill("input[name='username']", "osint_checker_99")
            time.sleep(1.5)
            
            page.fill("input[name='password']", "Password123!")
            time.sleep(2)  # Idő a validáció lefutásához
            
            content = page.content()
            
            # Extra várakozás zárás előtt, hogy látsd az eredményt a képernyőn
            time.sleep(2)
            browser.close()
            
            # Ellenőrizzük, hogy jelez-e a rendszer foglalt e-mail címet
            if "already use" in content.lower() or "már használatban" in content.lower() or "taken" in content.lower():
                return "[+] Instagram: Az e-mail már használatban van egy fióknál."
    except Exception:
        pass
        
    return None


def check_gravatar(email):
    """
    Gravatar modul, ami nemcsak a létezést, hanem a felhasználónevet is kinyeri.
    """
    email_hash = hashlib.md5(email.strip().lower().encode('utf-8')).hexdigest()
    url = f"https://www.gravatar.com/{email_hash}.json"
    
    try:
        response = requests.get(url, headers=get_random_headers(), timeout=5)
        if response.status_code == 200:
            data = response.json()
            entry = data.get("entry", [{}])[0]
            username = entry.get("preferredUsername", "Ismeretlen")
            profile_url = entry.get("profileUrl", f"https://gravatar.com/{email_hash}")
            return f"[+] Gravatar: Találat! | Felhasználónév: {username} | Profil: {profile_url}"
    except Exception:
        pass
    return None


# Modulok listája
MODULES = [
    ("Twitter/X", check_twitter),
    ("Instagram", check_instagram),
    ("Gravatar", check_gravatar)
]

# ==============================================================================
# FŐ PROGRAM
# ==============================================================================

def main():
    parser = argparse.ArgumentParser(description="Továbbfejlesztett edukációs OSINT keretrendszer.")
    parser.add_argument("-e", "--email", required=True, help="A vizsgálandó e-mail cím")
    args = parser.parse_args()
    
    target_email = args.email

    print(f"\n[i] Célpont: {target_email}")
    print("[i] Modulok futtatása véletlenszerű késleltetéssel...\n" + "="*50)

    found_count = 0

    for name, func in MODULES:
        print(f"[*] Ellenőrzés itt: {name}...", end="", flush=True)
        
        # Késleltetés a gyanús minták elkerülésére
        time.sleep(random.uniform(1.0, 2.0))
        
        result = func(target_email)
        if result:
            print(" Siker!")
            print(f"    {result}")
            found_count += 1
        else:
            print(" Nincs találat / Blokkolva.")

    print("="*50)
    print(f"[i] Vizsgálat vége. Összesen {found_count} találat.")

if __name__ == "__main__":
    main()
