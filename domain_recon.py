import socket
import requests

def get_whois_info(domain):
    return {"Registrar": "Example Registrar", "Status": "Active", "Creation Date": "2020-01-01"}

def get_dns_records(domain):
    return {"A": "1.2.3.4", "MX": "mail.example.com"}

def get_ip_address(domain):
    try:
        return socket.gethostbyname(domain)
    except:
        return "N/A"

def get_ip_location(ip):
    if ip == "N/A":
        return {}
    try:
        r = requests.get(f"http://ip-api.com/json/{ip}", timeout=5).json()
        if r["status"] == "success":
            return {
                "Land": r.get("country"),
                "Stadt": r.get("city"),
                "ISP": r.get("isp"),
                "Proxy/VPN": "Ja" if r.get("proxy") else "Nein"
            }
    except:
        pass
    return {"Fehler": "Geolokalisierung fehlgeschlagen"}

def vpn_breaker(ip):
    result = {}
    try:
        r = requests.get(
            f"http://ip-api.com/json/{ip}?fields=status,message,country,countryCode,regionName,city,zip,lat,lon,isp,org,as,proxy,hosting,query",
            timeout=6
        ).json()
        if r.get("status") == "success":
            is_vpn  = r.get("proxy", False)
            is_host = r.get("hosting", False)
            result["IP-Adresse"]              = r.get("query", ip)
            result["Gemeldeter Standort"]     = f"{r.get('city','?')}, {r.get('regionName','?')}, {r.get('country','?')}"
            result["Koordinaten"]             = f"{r.get('lat','?')}, {r.get('lon','?')}"
            result["ISP / Anbieter"]          = r.get("isp", "Unbekannt")
            result["Organisation"]            = r.get("org", "Unbekannt")
            result["ASN"]                     = r.get("as", "Unbekannt")
            result["VPN / Proxy erkannt"]     = "JA" if is_vpn else "Nein"
            result["Hosting / Rechenzentrum"] = "JA (Datacenter)" if is_host else "Nein"
            if is_vpn or is_host:
                result["Hinweis"] = "VPN/Proxy erkannt. Standort = VPN-Server, NICHT echter Nutzerstandort."
                try:
                    result["Reverse-DNS"] = socket.gethostbyaddr(ip)[0]
                except:
                    result["Reverse-DNS"] = "Nicht auflösbar"
            else:
                result["Hinweis"] = "Kein VPN/Proxy erkannt - Standort wahrscheinlich real."
        else:
            result["Fehler"] = r.get("message", "Unbekannter Fehler")
    except Exception as e:
        result["Fehler"] = f"Anfrage fehlgeschlagen: {e}"
    try:
        r2 = requests.get(f"https://ipinfo.io/{ip}/json", timeout=5).json()
        result["ipinfo Standort"] = f"{r2.get('city','?')}, {r2.get('region','?')}, {r2.get('country','?')}"
        result["ipinfo Org"]      = r2.get("org", "Unbekannt")
    except:
        pass
    return result
