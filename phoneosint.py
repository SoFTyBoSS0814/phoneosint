#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import requests
import sys
import time
import random

# Különböző valós böngésző User-Agent字符串ek, hogy ne egyformázat küldjünk
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
    Instagram ellenőrzési modul vázlat.
    """
    url = "https://www.instagram.com/accounts/web_create_ajax/attempt/"
    headers = get_random_headers()
    headers["X-Requested-With"] = "XMLHttpRequest"
    headers["Referer"] = "https://www.instagram.com/accounts/emailsignup/"
    
    data = {
        "email": email,
        "username": "osint_test_user_99",
        "first_name": "Test",
        "opt_into_one_tap": "false"
    }

    try:
        response = requests.post(url, data=data, headers=headers, timeout=5)
        if response.status_code == 200:
            res_json = response.json()
            if "email_is_taken" in res_json.get("errors", {}):
                return "[+] Instagram: Az e-mail már használatban van egy fióknál."
    except requests.exceptions.RequestException:
        pass
    return None


def check_gravatar(email):
    """
    Gravatar modul (Ez a valóságban is teljesen stabilan működik, 
    mivel nyilvános API-t használ).
    """
    import hashlib
    email_hash = hashlib.md5(email.strip().lower().encode('utf-8')).hexdigest()
    url = f"https://www.gravatar.com/{email_hash}.json"
    
    try:
        response = requests.get(url, headers=get_random_headers(), timeout=5)
        if response.status_code == 200:
            return f"[+] Gravatar: Profil megtalálva -> https://gravatar.com/{email_hash}"
    except requests.exceptions.RequestException:
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
    print("[i] Modulok futtatása véletlenszerű késleltetéssel és fejlécekkel...\n" + "="*50)

    found_count = 0

    for name, func in MODULES:
        print([*] Ellenőrzés itt: {name}...", end="", flush=True)
        
        # Késleltetés elhelyezése a kérések között (elkerüli az azonnali gyanús tiltást)
        time.sleep(random.uniform(1.0, 2.5))
        
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
