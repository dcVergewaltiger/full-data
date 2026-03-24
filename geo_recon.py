import requests
import socket

def gps_to_map(lat: float, lon: float) -> dict:
    """Konvertiert GPS-Koordinaten in Map-Links."""
    return {
        "Koordinaten":          f"{lat}, {lon}",
        "Google Maps":          f"https://www.google.com/maps?q={lat},{lon}",
        "Google Maps Satellit": f"https://www.google.com/maps/@{lat},{lon},15z/data=!3m1!1e3",
        "OpenStreetMap":        f"https://www.openstreetmap.org/?mlat={lat}&mlon={lon}&zoom=15",
        "What3Words":           f"https://what3words.com/map?lat={lat}&lng={lon}",
        "Bing Maps":            f"https://www.bing.com/maps?cp={lat}~{lon}&lvl=15",
    }

def phone_spam_score(phone: str) -> dict:
    """Gibt Spam-Score Links für eine Telefonnummer zurück."""
    clean = phone.replace("+", "").replace(" ", "").replace("-", "")
    intl  = phone if phone.startswith("+") else "+" + clean
    return {
        "Tellows (Spam-Score)":  f"https://www.tellows.de/num/{clean}",
        "WerRuftAn":             f"https://www.wer-ruft-an.de/telefon/{clean}",
        "Clever Dialer":         f"https://www.cleverdialer.de/telefonnummer/{clean}",
        "Truecaller":            f"https://www.truecaller.com/search/de/{clean}",
        "SpamCalls":             f"https://spamcalls.net/en/search?number={clean}",
        "Should I Answer":       f"https://www.shouldianswer.net/phone-number/{clean}",
        "Sync.me":               f"https://sync.me/search/?number={clean}",
        "NumLookup":             f"https://www.numlookup.com/phone-number-lookup/{clean}",
    }

def ip_network_scan(ip: str) -> dict:
    """Gibt Netzwerk-Scan Links und Basis-Infos für eine IP zurück."""
    result = {}
    try:
        r = requests.get(
            f"http://ip-api.com/json/{ip}?fields=status,country,regionName,city,isp,org,as,proxy,hosting,query",
            timeout=6
        ).json()
        if r.get("status") == "success":
            result["IP-Adresse"]   = r.get("query", ip)
            result["Land"]         = r.get("country", "?")
            result["Region"]       = r.get("regionName", "?")
            result["Stadt"]        = r.get("city", "?")
            result["ISP"]          = r.get("isp", "?")
            result["Organisation"] = r.get("org", "?")
            result["ASN"]          = r.get("as", "?")
            result["Proxy/VPN"]    = "Ja" if r.get("proxy") else "Nein"
            result["Hosting/DC"]   = "Ja" if r.get("hosting") else "Nein"
    except Exception as e:
        result["Fehler"] = str(e)
    try:
        hostname = socket.gethostbyaddr(ip)[0]
        result["Hostname (rDNS)"] = hostname
    except:
        result["Hostname (rDNS)"] = "Nicht auflösbar"
    result["Shodan"]          = f"https://www.shodan.io/host/{ip}"
    result["Censys"]          = f"https://search.censys.io/hosts/{ip}"
    result["VirusTotal"]      = f"https://www.virustotal.com/gui/ip-address/{ip}"
    result["AbuseIPDB"]       = f"https://www.abuseipdb.com/check/{ip}"
    result["IPVoid"]          = f"https://www.ipvoid.com/ip-blacklist-check/?ip={ip}"
    result["Greynoise"]       = f"https://viz.greynoise.io/ip/{ip}"
    result["Threatbook"]      = f"https://threatbook.io/ip/{ip}"
    return result

def address_lookup(address: str) -> dict:
    """Gibt Karten- und Personen-Such-Links für eine Adresse zurück."""
    q = requests.utils.quote(address)
    return {
        "Google Maps":          f"https://www.google.com/maps/search/{q}",
        "Google Streetview":    f"https://www.google.com/maps?q={q}&layer=c",
        "OpenStreetMap":        f"https://www.openstreetmap.org/search?query={q}",
        "Bing Maps":            f"https://www.bing.com/maps?q={q}",
        "Das Örtliche":         f"https://www.dasoertliche.de/rubriken/?kw={q}",
        "Telefonbuch.de":       f"https://www.telefonbuch.de/suche/personen?q={q}",
        "11880.com":            f"https://www.11880.com/suche/{q}/",
        "Google Dork Adresse":  f"https://www.google.com/search?q=%22{q}%22",
        "Immobilienscout":      f"https://www.immobilienscout24.de/Suche/de/{q}",
    }

def fake_profile_check(image_url: str = "") -> dict:
    """Gibt Links zur Fake-Profil und KI-Bild-Erkennung zurück."""
    result = {
        "Hive Moderation (KI-Bild)": "https://hivemoderation.com/ai-generated-content-detection",
        "AI or Not":                 "https://www.aiornot.com/",
        "Illuminarty":               "https://illuminarty.ai/",
        "FotoForensics (EXIF/ELA)":  "https://fotoforensics.com/",
        "Ghiro (Forensik)":          "http://www.getghiro.org/",
        "InVID WeVerify":            "https://weverify.eu/tools/",
        "TinEye (Reverse)":          "https://tineye.com/",
        "PimEyes (Gesicht)":         "https://pimeyes.com/en",
    }
    if image_url:
        q = requests.utils.quote(image_url)
        result["Google Lens"] = f"https://lens.google.com/uploadbyurl?url={q}"
        result["Yandex Reverse"] = f"https://yandex.com/images/search?url={q}&rpt=imageview"
    return result
