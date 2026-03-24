import requests

def lookup_phone(phone_number):
    clean = phone_number.replace("+", "").replace(" ", "").replace("-", "")
    return {
        "Nummer":     phone_number,
        "WhatsApp":   "https://wa.me/" + clean,
        "Telegram":   "Suche in App nach: " + phone_number,
        "Truecaller": "https://www.truecaller.com/search/de/" + clean,
        "Sync.me":    "https://sync.me/search/?number=" + clean,
    }

def check_account_existence(email):
    return {
        "Google":   "https://accounts.google.com/signin/v2/identifier?identifier=" + email,
        "Apple":    "https://iforgot.apple.com/password/verify/appleid",
        "Facebook": "https://www.facebook.com/login/identify/?ctx=recover&email=" + email,
        "Twitter":  "https://twitter.com/i/flow/password_reset",
    }

def check_breaches(email):
    return {
        "Have I Been Pwned": f"https://haveibeenpwned.com/account/{email}",
        "DeHashed":          f"https://dehashed.com/search?query={email}",
        "IntelligenceX":     f"https://intelx.io/?s={email}",
        "LeakCheck":         f"https://leakcheck.io/?query={email}",
        "Snusbase":          "https://snusbase.com/",
    }

def password_finder(email):
    clean = email.strip()
    results = {
        "LeakCheck.io":    f"https://leakcheck.io/?query={clean}",
        "DeHashed":        f"https://dehashed.com/search?query={clean}",
        "Snusbase":        "https://snusbase.com/",
        "IntelligenceX":   f"https://intelx.io/?s={clean}",
        "HIBP Breaches":   f"https://haveibeenpwned.com/account/{clean}",
        "BreachDirectory": "https://breachdirectory.org/",
        "Scylla.sh":       f"https://scylla.sh/search?q={clean}",
        "ProxyNova COMB":  f"https://www.proxynova.com/tools/comb/?search={clean}",
    }
    try:
        r = requests.get(
            f"https://breachdirectory.p.rapidapi.com/?func=auto&term={clean}",
            headers={"X-RapidAPI-Host": "breachdirectory.p.rapidapi.com"},
            timeout=5
        ).json()
        if r.get("success") and r.get("result"):
            for i, entry in enumerate(r["result"][:5]):
                src   = entry.get("sources", ["?"])[0]
                plain = entry.get("password", "")
                sha1  = entry.get("sha1", "")
                val = f"Quelle: {src}"
                if plain:
                    val += f" | Passwort: {plain}"
                elif sha1:
                    val += f" | SHA1: {sha1[:20]}..."
                results[f"Leak-Fund {i+1}"] = val
    except:
        pass
    return results
