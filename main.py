import argparse
import json
from tabulate import tabulate
from domain_recon import get_whois_info, get_dns_records, get_ip_address, get_ip_location
from social_recon import check_social_media, lookup_discord_id, search_real_name
from phone_recon import lookup_phone, check_account_existence, check_breaches
from media_recon import get_exif_data

def main():
    parser = argparse.ArgumentParser(description="OSINT Tool - Digitale Spurensuche (Pro Version)")
    parser.add_argument("-d", "--domain", help="Domain für WHOIS- und DNS-Recherche")
    parser.add_argument("-u", "--username", help="Benutzername für Social-Media-Suche")
    parser.add_argument("-i", "--discord-id", help="Discord-ID (Zahlenreihe) für Recherche")
    parser.add_argument("-n", "--name", help="Echter Name für Google Dorks und Profile")
    parser.add_argument("-p", "--phone", help="Telefonnummer (z. B. +49123456789)")
    parser.add_argument("-e", "--email", help="E-Mail für Google/Apple Account-Check & Breaches")
    parser.add_argument("-m", "--media", help="Pfad zu einer Bilddatei für Metadaten-Extraktion")
    parser.add_argument("-o", "--output", help="Ausgabedatei (JSON)", default="osint_report.json")

    args = parser.parse_args()
    report = {}

    if args.domain:
        print(f"[*] Starte Domain-Recherche für: {args.domain}")
        whois_data = get_whois_info(args.domain)
        dns_data = get_dns_records(args.domain)
        ip = get_ip_address(args.domain)
        ip_location = get_ip_location(ip)
        report["domain"] = {"whois": whois_data, "dns": dns_data, "ip": ip, "location": ip_location}
        print(f"\n--- Domain- & IP-Infos ---\n", tabulate([["IP", ip]] + list(ip_location.items()), tablefmt="grid"))

    if args.username:
        print(f"\n[*] Suche nach Social-Media-Profilen für: {args.username} (inkl. Variationen)")
        social_data = check_social_media(args.username)
        print("\n[+] Ergebnisse:")
        for platform, result in social_data.items():
            print(f"{platform}: {result}")
        report["social_media"] = social_data

    if args.discord_id:
        print(f"\n[*] Discord-ID Recherche für: {args.discord_id}")
        discord_data = lookup_discord_id(args.discord_id)
        print(f"\n--- Discord Lookup ---\n", tabulate(discord_data.items(), tablefmt="grid"))
        report["discord"] = discord_data

    if args.name:
        print(f"\n[*] Suche nach echtem Namen: {args.name}")
        name_data = search_real_name(args.name)
        print(f"\n--- Namens-Suche ---\n", tabulate(name_data.items(), tablefmt="grid"))
        report["real_name"] = name_data

    if args.phone:
        print(f"\n[*] Telefonnummern-Recherche für: {args.phone}")
        phone_data = lookup_phone(args.phone)
        print(f"\n--- Telefon-Recherche ---\n", tabulate(phone_data.items(), tablefmt="grid"))
        report["phone"] = phone_data

    if args.email:
        print(f"\n[*] Account- & Breach-Check für: {args.email}")
        email_data = check_account_existence(args.email)
        breach_data = check_breaches(args.email)
        print(f"\n--- Account-Check ---\n", tabulate(email_data.items(), tablefmt="grid"))
        print(f"\n--- Breach-Check ---\n", tabulate(breach_data.items(), tablefmt="grid"))
        report["accounts"] = email_data
        report["breaches"] = breach_data

    if args.media:
        print(f"\n[*] Metadaten-Extraktion für: {args.media}")
        media_data = get_exif_data(args.media)
        print(f"\n--- Bild-Metadaten ---\n", tabulate(media_data.items(), tablefmt="grid"))
        report["media"] = media_data

    if report:
        with open(args.output, "w") as f:
            json.dump(report, f, indent=4)
        print(f"\n[!] Bericht gespeichert in {args.output}")

if __name__ == "__main__":
    main()
