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
    if ip == "N/A": return {}
    try:
        # Nutzung einer kostenlosen API für Geolokalisierung
        response = requests.get(f"http://ip-api.com/json/{ip}", timeout=5).json()
        if response["status"] == "success":
            return {
                "Land": response.get("country"),
                "Stadt": response.get("city"),
                "ISP": response.get("isp"),
                "Proxy/VPN": "Unbekannt (Erfordert Pro-API)"
            }
    except:
        pass
    return {"Fehler": "Geolokalisierung fehlgeschlagen"}
