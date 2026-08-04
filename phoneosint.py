#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import requests
import time
import random
import hashlib
import sys

# Valós böngésző User-Agent stringek a blokkolások elkerülésére
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
# SHERLOCK-STÍLUSÚ SZOLGÁLTATÁSI ADATBÁZIS (E-mail alapon)
# ==============================================================================
# Minden modul itt van definiálva: URL, módszer, paraméterek és a siker feltételei.
SERVICES = {
    "Twitter/X": {
        "url": "https://api.twitter.com/i/users/email_available.json",
        "method": "GET",
        "params": lambda email: {"email": email},
        "check": lambda res: res.status_code == 200 and (res.json().get("taken") == True or res.json().get("valid") == False),
        "message": "Az e-mail címhez tartozik regisztrált fiók."
    },
    "Instagram": {
        "url": "https://www.instagram.com/api/v1/users/check_email/",
        "method": "POST",
        "headers": {
            "X-IG-App-ID": "936619743392459",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": "https://www.instagram.com/accounts/emailsignup/"
        },
        "data": lambda email: {"email": email},
        "check": lambda res: res.status_code == 200 and (res.json().get("available") == False or res.json().get("confirmed") == True),
        "message": "Az e-mail már használatban van egy fióknál."
    },
    "Gravatar": {
        "url": lambda email: f"https://www.gravatar.com/{hashlib.md5(email.strip().lower().encode('utf-8')).hexdigest()}.json",
        "method": "GET",
        "check": lambda res: res.status_code == 200,
        "message": lambda res: f"Találat! | Felhasználónév: {res.json().get('entry', [{}])[0].get('preferredUsername', 'Ismeretlen')}"
    }
}

# ==============================================================================
# MOTOR (WORKER)
# ==============================================================================

def inspect_target(service_name, config, email):
    """
    Univerzális ellenőrző függvény, amely a konfiguráció alapján futtatja a lekérdezést.
    """
    headers = get_random_headers()
    if "headers" in config:
        headers.update(config["headers"])

    try:
        # URL meghatározása (lehet statikus string vagy dinamikus lambda)
        target_url = config["url"](email) if callable(config["url"]) else config["url"]
        
        # Paraméterek vagy adatok összeállítása
        params = config["params"](email) if "params" in config else None
        data = config["data"](email) if "data" in config else None

        # HTTP kérés indítása a megadott metódussal
        if config["method"] == "GET":
            response = requests.get(target_url, headers=headers, params=params, timeout=6)
        elif config["method"] == "POST":
            response = requests.post(target_url, headers=headers, data=data, timeout=6)
        else:
            return None

        # Eredmény kiértékelése a konfigurált feltétel (check) alapján
        if config["check"](response):
            msg_conf = config["message"]
            if callable(msg_conf):
                return msg_conf(response)
            return msg_conf

    except requests.exceptions.RequestException:
        pass
    except Exception:
        pass

    return None

# ==============================================================================
# FŐ PROGRAM
# ==============================================================================

def main():
    parser = argparse.ArgumentParser(description="Mini-Sherlock alapú e-mail OSINT keretrendszer.")
    parser.add_argument("-e", "--email", required=True, help="A vizsgálandó e-mail cím")
    args = parser.parse_args()
    
    target_email = args.email

    print(f"\n[i] Célpont: {target_email}")
    print(f"[i] Modulok betöltve: {len(SERVICES)} db")
    print("[i] Vizsgálat indítása a háttérben...\n" + "="*50)

    found_count = 0

    for name, config in SERVICES.items():
        print(f"[*] Keresés itt: {name:<12} ...", end="", flush=True)
        time.sleep(random.uniform(0.3, 0.6))
        
        result = inspect_target(name, config, target_email)
        
        if result:
            print(" [TALÁLAT]")
            print(f"    └── {result}")
            found_count += 1
        else:
            print(" [Nincs találat]")

    print("="*50)
    print(f"[i] Keresés vége. Összesen {found_count} találat.")

if __name__ == "__main__":
    main()
