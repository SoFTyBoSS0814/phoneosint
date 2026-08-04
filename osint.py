#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
import requests
import random
import time
import sys

# Valós böngésző User-Agent stringek a blokkolások elkerülésére
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0"
]

def get_random_headers():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept-Language": "hu-HU,hu;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Connection": "keep-alive"
    }

def load_database(filename="data.json"):
    """Betölti és elemzi a lokális Sherlock data.json fájlt."""
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"[!] Hiba: A(z) '{filename}' fájl nem található a mappában!")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"[!] Hiba: A(z) '{filename}' fájl nem érvényes JSON formátumú!")
        sys.exit(1)

def check_profile(site_name, site_data, username):
    """
    Feldolgozza az adott oldal szabályait a data.json alapján,
    és lefuttatja a HTTP kérést.
    """
    url_template = site_data.get("url")
    if not url_template:
        return False, None

    target_url = url_template.format(username)
    error_type = site_data.get("errorType", "status_code")
    
    headers = get_random_headers()
    # Ha a JSON-ben meg vannak adva extra fejlécek az adott oldalhoz
    if "headers" in site_data and isinstance(site_data["headers"], dict):
        headers.update(site_data["headers"])

    try:
        # A Sherlock alapértelmezetten GET kérést használ, de figyelembe vesszük a JSON-t ha mást kér
        method = site_data.get("requestType", "GET").upper()
        
        if method == "POST":
            response = requests.post(target_url, headers=headers, timeout=6, allow_redirects=True)
        else:
            response = requests.get(target_url, headers=headers, timeout=6, allow_redirects=True)

        # 1. Státuszkód alapú ellenőrzés (pl. 200 = létezik, 404 = nem létezik)
        if error_type == "status_code":
            # Alapértelmezett hiba státusz a 404
            error_code = site_data.get("errorCod", 404)
            if response.status_code == 200:
                return True, target_url

        # 2. Üzenet alapú ellenőrzés (ha a válaszoldal tartalmaz egy adott hibaüzenetet, akkor nincs fiók)
        elif error_type == "message":
            error_msg = site_data.get("errorMsg")
            if error_msg:
                # Ha a hibaüzenet NINCS benne a válaszban, akkor valószínűleg létezik a profil
                if error_msg not in response.text and response.status_code == 200:
                    return True, target_url

        # 3. Válasz URL / Redirect alapú ellenőrzés
        elif error_type == "response_url":
            if response.status_code == 200:
                return True, target_url

    except requests.exceptions.RequestException:
        # Hálózati hiba, időtúllépés esetén csendesen továbblépünk
        pass
    except Exception:
        pass

    return False, None

def main():
    parser = argparse.ArgumentParser(description="Mini-Sherlock lokális JSON alapú OSINT névkereső.")
    parser.add_argument("-u", "--username", required=True, help="A keresett felhasználónév")
    parser.add_argument("-j", "--json", default="data.json", help="A data.json fájl elérési útja (alapértelmezett: data.json)")
    args = parser.parse_args()
    
    target_user = args.username
    database = load_database(args.json)

    print(f"\n[i] Célpont felhasználónév: {target_user}")
    print(f"[i] Adatbázis betöltve: {len(database)} db platform elemezve.")
    print("[i] Keresés indítása a háttérben...\n" + "=" * 60)

    found_count = 0
    start_time = time.time()

    for site_name, site_data in database.items():
        print(f"[*] Keresés itt: {site_name:<18} ...", end="", flush=True)
        
        success, url = check_profile(site_name, site_data, target_user)
        
        if success:
            print(" [TALÁLAT]")
            print(f"    └── {url}")
            found_count += 1
        else:
            print(" [Nincs]")
        
        # Minimális szünet a kérések között a túlterhelés elkerülésére
        time.sleep(0.05)

    elapsed_time = round(time.time() - start_time, 2)
    print("=" * 60)
    print(f"[i] Keresés vége. Találatok: {found_count} db | Időtartam: {elapsed_time}s")

if __name__ == "__main__":
    main()
