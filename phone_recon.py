import requests

def lookup_phone(phone_number):
    results = {
        "Nummer": phone_number,
        "WhatsApp": "Prüfe manuell: https://wa.me/" + phone_number.replace("+", "").replace(" ", ""),
        "Telegram": "Suche in App nach: " + phone_number
    }
    return results

def check_account_existence(email):
    results = {
        "Google": "Möglich (Prüfe via: https://accounts.google.com/signin/v2/identifier?identifier=" + email + ")",
        "Apple": "Möglich (Prüfe via: https://iforgot.apple.com/password/verify/appleid)"
    }
    return results

def check_breaches(email):
    # Prüfung auf Datenlecks (via Have I Been Pwned API oder ähnliche)
    # Da HIBP einen API-Key erfordert, nutzen wir hier einen Link für den Nutzer.
    return {
        "Have I Been Pwned": f"https://haveibeenpwned.com/account/{email}",
        "DeHashed": f"https://dehashed.com/search?query={email}",
        "IntelligenceX": f"https://intelx.io/?s={email}"
    }
