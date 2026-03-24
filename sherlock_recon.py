import requests

PLATFORMS = {
    "Instagram":    "https://www.instagram.com/{}/",
    "Twitter/X":    "https://twitter.com/{}",
    "TikTok":       "https://www.tiktok.com/@{}",
    "YouTube":      "https://www.youtube.com/@{}",
    "Reddit":       "https://www.reddit.com/user/{}",
    "GitHub":       "https://github.com/{}",
    "GitLab":       "https://gitlab.com/{}",
    "Pinterest":    "https://www.pinterest.com/{}/",
    "Twitch":       "https://www.twitch.tv/{}",
    "Steam":        "https://steamcommunity.com/id/{}",
    "Spotify":      "https://open.spotify.com/user/{}",
    "SoundCloud":   "https://soundcloud.com/{}",
    "Flickr":       "https://www.flickr.com/people/{}",
    "Tumblr":       "https://{}.tumblr.com",
    "Medium":       "https://medium.com/@{}",
    "DevTo":        "https://dev.to/{}",
    "Keybase":      "https://keybase.io/{}",
    "HackerNews":   "https://news.ycombinator.com/user?id={}",
    "ProductHunt":  "https://www.producthunt.com/@{}",
    "Patreon":      "https://www.patreon.com/{}",
    "OnlyFans":     "https://onlyfans.com/{}",
    "Linktree":     "https://linktr.ee/{}",
    "Cashapp":      "https://cash.app/${}",
    "Venmo":        "https://venmo.com/{}",
    "Behance":      "https://www.behance.net/{}",
    "Dribbble":     "https://dribbble.com/{}",
    "Fiverr":       "https://www.fiverr.com/{}",
    "Freelancer":   "https://www.freelancer.com/u/{}",
    "Replit":       "https://replit.com/@{}",
    "CodePen":      "https://codepen.io/{}",
    "Stackoverflow":"https://stackoverflow.com/users/{}",
    "Vimeo":        "https://vimeo.com/{}",
    "Dailymotion":  "https://www.dailymotion.com/{}",
    "Telegram":     "https://t.me/{}",
    "Signal":       "https://signal.me/#p/{}",
    "Discord":      "https://discord.com/users/{}",
    "Snapchat":     "https://www.snapchat.com/add/{}",
    "VK":           "https://vk.com/{}",
    "OK.ru":        "https://ok.ru/{}",
    "Xing":         "https://www.xing.com/profile/{}",
    "LinkedIn":     "https://www.linkedin.com/in/{}",
    "Facebook":     "https://www.facebook.com/{}",
    "Ask.fm":       "https://ask.fm/{}",
    "Quora":        "https://www.quora.com/profile/{}",
    "Wattpad":      "https://www.wattpad.com/user/{}",
    "Roblox":       "https://www.roblox.com/user.aspx?username={}",
    "Minecraft":    "https://namemc.com/profile/{}",
    "Chess.com":    "https://www.chess.com/member/{}",
    "Duolingo":     "https://www.duolingo.com/profile/{}",
    "Goodreads":    "https://www.goodreads.com/{}",
    "Last.fm":      "https://www.last.fm/user/{}",
}

def sherlock_search(username: str) -> dict:
    """Prüft Benutzername auf 50+ Plattformen und gibt Links zurück."""
    username = username.strip()
    results = {}
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})
    for platform, url_template in PLATFORMS.items():
        url = url_template.format(username)
        results[platform] = url
    return results

def dork_generator(query: str, query_type: str = "name") -> dict:
    """Generiert Google Dork Suchanfragen für verschiedene Typen."""
    q = requests.utils.quote(query)
    dorks = {}
    if query_type == "email":
        dorks["Google – Direkt"]         = f"https://www.google.com/search?q=%22{q}%22"
        dorks["Google – Passwort-Leaks"] = f"https://www.google.com/search?q=%22{q}%22+%22password%22+OR+%22leak%22"
        dorks["Google – Social Media"]   = f"https://www.google.com/search?q=%22{q}%22+site%3Ainstagram.com+OR+site%3Atwitter.com+OR+site%3Afacebook.com"
        dorks["Google – Dokumente"]      = f"https://www.google.com/search?q=%22{q}%22+filetype%3Apdf+OR+filetype%3Adoc"
        dorks["Bing – Direkt"]           = f"https://www.bing.com/search?q=%22{q}%22"
        dorks["DuckDuckGo"]              = f"https://duckduckgo.com/?q=%22{q}%22"
        dorks["Yandex"]                  = f"https://yandex.com/search/?text={q}"
        dorks["IntelligenceX"]           = f"https://intelx.io/?s={q}"
        dorks["Pastebin-Suche"]          = f"https://www.google.com/search?q=%22{q}%22+site%3Apastebin.com"
    elif query_type == "phone":
        dorks["Google – Direkt"]         = f"https://www.google.com/search?q=%22{q}%22"
        dorks["Google – WhatsApp"]       = f"https://www.google.com/search?q=%22{q}%22+whatsapp"
        dorks["Google – Telefonbuch"]    = f"https://www.google.com/search?q=%22{q}%22+telefonbuch+OR+%22phone+number%22"
        dorks["Truecaller"]              = f"https://www.truecaller.com/search/de/{query.replace('+','').replace(' ','')}"
        dorks["Sync.me"]                 = f"https://sync.me/search/?number={query.replace('+','').replace(' ','')}"
        dorks["Bing"]                    = f"https://www.bing.com/search?q=%22{q}%22"
    else:  # name
        dorks["Google – Direkt"]         = f"https://www.google.com/search?q=%22{q}%22"
        dorks["Google – Social Media"]   = f"https://www.google.com/search?q=%22{q}%22+site%3Ainstagram.com+OR+site%3Atwitter.com+OR+site%3Afacebook.com+OR+site%3Alinkedin.com"
        dorks["Google – Bilder"]         = f"https://www.google.com/search?q=%22{q}%22&tbm=isch"
        dorks["Google – Nachrichten"]    = f"https://www.google.com/search?q=%22{q}%22&tbm=nws"
        dorks["Google – Dokumente"]      = f"https://www.google.com/search?q=%22{q}%22+filetype%3Apdf+OR+filetype%3Adoc"
        dorks["LinkedIn-Suche"]          = f"https://www.linkedin.com/search/results/people/?keywords={q}"
        dorks["Facebook-Suche"]          = f"https://www.facebook.com/search/people/?q={q}"
        dorks["Bing – Direkt"]           = f"https://www.bing.com/search?q=%22{q}%22"
        dorks["DuckDuckGo"]              = f"https://duckduckgo.com/?q=%22{q}%22"
        dorks["Yandex"]                  = f"https://yandex.com/search/?text={q}"
        dorks["Pastebin"]                = f"https://www.google.com/search?q=%22{q}%22+site%3Apastebin.com"
    return dorks

def reverse_image_links(image_url: str = "") -> dict:
    """Generiert Reverse Image Search Links."""
    links = {}
    if image_url:
        q = requests.utils.quote(image_url)
        links["Google Images"]  = f"https://lens.google.com/uploadbyurl?url={q}"
        links["Yandex Images"]  = f"https://yandex.com/images/search?url={q}&rpt=imageview"
        links["Bing Visual"]    = f"https://www.bing.com/images/search?q=imgurl:{q}&view=detailv2&iss=sbi"
        links["TinEye"]         = f"https://tineye.com/search?url={q}"
    links["Google Lens (Upload)"]  = "https://lens.google.com/"
    links["Yandex (Upload)"]       = "https://yandex.com/images/"
    links["TinEye (Upload)"]       = "https://tineye.com/"
    links["PimEyes (Gesicht)"]     = "https://pimeyes.com/en"
    links["FaceCheck.ID"]          = "https://facecheck.id/"
    links["Search4Faces"]          = "https://search4faces.com/"
    links["Bing Visual Search"]    = "https://www.bing.com/visualsearch"
    return links
