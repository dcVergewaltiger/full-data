import requests

def check_social_media(username):
    # Basis-Variationen des Namens erstellen
    variations = [
        username,
        f"{username}123",
        f"{username}_",
        f"{username}.",
        f"the{username}"
    ]
    
    platforms = {
        "GitHub": "https://github.com/",
        "Twitter": "https://twitter.com/",
        "Instagram": "https://instagram.com/",
        "Reddit": "https://www.reddit.com/user/",
        "Twitch": "https://www.twitch.tv/",
        "Steam": "https://steamcommunity.com/id/"
    }
    
    results = {}
    
    # Prüfe die Haupt-Variationen (für eine schnellere Suche nur die ersten 3)
    for v in variations[:3]:
        for platform, base_url in platforms.items():
            url = f"{base_url}{v}"
            try:
                response = requests.get(url, timeout=3)
                if response.status_code == 200:
                    results[f"{platform} ({v})"] = f"Gefunden: {url}"
            except:
                pass
                
    # Discord & Wayback Machine Links (Immer anzeigen)
    results["Discord (Lookup)"] = f"https://discordlookup.com/user/{username}"
    results["Wayback Machine"] = f"https://web.archive.org/web/*/{username}*"
        
    return results

def lookup_discord_id(discord_id):
    lookup_urls = {
        "Discord.id": f"https://discord.id/?id={discord_id}",
        "DiscordLookup": f"https://discordlookup.com/user/{discord_id}",
        "Lanyard": f"https://api.lanyard.rest/v1/users/{discord_id}"
    }
    results = {}
    for service, url in lookup_urls.items():
        results[service] = f"Prüfe: {url}"
    return results

def search_real_name(full_name):
    query = full_name.replace(" ", "+")
    dorks = {
        "Google Suche": f"https://www.google.com/search?q=\"{query}\"",
        "Facebook": f"https://www.facebook.com/public/{query}",
        "LinkedIn": f"https://www.linkedin.com/pub/dir?firstName={full_name.split()[0]}&lastName={full_name.split()[-1]}",
        "Das Örtliche (DE)": f"https://www.dasoertliche.de/?form_name=search_nat&kw={query}"
    }
    return dorks
