#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import requests
import sys

# ==============================================================================
# MODULOK / WEBOLDALAK DEFINÍCIÓJA
# 
# Megjegyzés edukációs célra: A legtöbb modern platform (Facebook, Twitter/X, 
# Instagram, Snapchat) komplex védelemmel (Cloudflare, CAPTCHA, rate-limiting) 
# vagy mobilalkalmazás-specifikus API-kkal rendelkezik. Az alábbi függvények 
# demonstrációs / vázlat szinten mutatják be, hogyan építhetők be a lekérdezések.
# ==============================================================================

def check_twitter(email):
    """
    Twitter / X e-mail ellenőrzési vázlat.
    A Twitter regisztrációs/jelszó-visszaállítási felülete ellenőrzi, hogy 
    létezik-e az e-mail cím.
    """
    url = "https://api.twitter.com/i/users/email_available.json" # Példa endpoint
    params = {"email": email}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "X-Twitter-Active-User": "yes",
        "X-Requested-With": "XMLHttpRequest"
    }

    try:
        # A valóságban itt szükség lehet tokenekre vagy pontosabb API fejlécekre
        response = requests.get(url, params=params, headers=headers, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            # Ha a valid kulcs hamis vagy taken, akkor létezik a fiók
            if data.get("taken") == True or data.get("valid") == False:
                return "[+] Twitter/X: Fiók találat (az e-mailhez tartozik regisztráció)."
    except Exception:
        pass
    
    return None


def check_instagram(email):
    """
    Instagram e-mail ellenőrzési vázlat.
    Az Instagram webes regisztrációs felülete JSON választ ad arra, 
    hogy az e-mail cím regisztrálva van-e már.
    """
    url = "https://www.instagram.com/accounts/web_create_ajax/attempt/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": "https://www.instagram.com/accounts/emailsignup/"
    }
    data = {
        "email": email,
        "username": "testuser123456789",
        "first_name": "Test",
        "opt_into_one_tap": "false"
    }

    try:
        response = requests.post(url, data=data, headers=headers, timeout=5)
        if response.status_code == 200:
            res_json = response.json()
            # Ha az e-mail már foglalt, az Instagram hibaüzenetet ad vissza rá
            if "email_is_taken" in res_json.get("errors", {}):
                return "[+] Instagram: Fiók találat (az e-mail már használatban van)."
    except Exception:
        pass

    return None


def check_facebook(email):
    """
    Facebook fiókkereső / regisztrációs ellenőrzés vázlat.
    """
    # A Facebook erős védelemmel (CAPTCHA / block) szűri az automatizált kéréseket,
    # ezért ez a modul saját szerverről vagy védelem nélkül gyakran hibára futhat.
    url = "https://www.facebook.com/login/identify/?ctx=recover"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    try:
        # Itt a Facebook fiókfelismerő oldalát kellene parselni (pl. BeautifulSoup-pal)
        # response = requests.get(url, headers=headers, timeout=5)
        pass
    except Exception:
        pass

    return None


def check_snapchat(email):
    """
    Snapchat e-mail ellenőrzési vázlat.
    """
    url = "https://accounts.snapchat.com/accounts/merlin/login"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

    try:
        # A Snapchat belső API-ja vagy webes felülete hasonló logikát használ
        pass
    except Exception:
        pass

    return None


# Fő lista, ami összegyűjti az összes ellenőrző funkciót
MODULES = [
    check_twitter,
    check_instagram,
    check_facebook,
    check_snapchat,
]


# ==============================================================================
# FŐ PROGRAM LOGIKA
# ==============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Oktatási célú OSINT e-mail ellenőrző keretrendszer (Social Media modulokkal).",
        usage="python osint_tool.py -e pelda@email.com"
    )
    parser.add_argument("-e", "--email", required=True, help="A vizsgálandó e-mail cím")

    args = parser.parse_args()
    target_email = args.email

    print(f"\n[*] Célpont e-mail: {target_email}")
    print("[*] Keresés indítása a közösségi oldalakon...\n" + "-" * 50)

    found_results = 0

    for mod in MODULES:
        result = mod(target_email)
        if result:
            print(result)
            found_results += 1
        else:
            print(f"[-] {mod.__name__}: Nincs találat vagy a szolgáltatás blokkolta a kérést.")

    print("-" * 50)
    print(f"[*] Keresés kész. Összesen {found_results} pozitív találat érkezett.")

if __name__ == "__main__":
    main()
