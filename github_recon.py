import requests

def github_user_recon(username: str) -> dict:
    username = username.strip()
    result = {}
    headers = {"Accept": "application/vnd.github.v3+json",
               "User-Agent": "OSINT-Tool/1.0"}
    try:
        r = requests.get(f"https://api.github.com/users/{username}", headers=headers, timeout=8).json()
        if r.get("message") == "Not Found":
            return {"Fehler": f"GitHub-Nutzer '{username}' nicht gefunden."}
        result["Name"]              = r.get("name") or "Nicht angegeben"
        result["Bio"]               = r.get("bio") or "Keine Bio"
        result["Standort"]          = r.get("location") or "Nicht angegeben"
        result["E-Mail (öffentl.)"] = r.get("email") or "Nicht öffentlich"
        result["Firma"]             = r.get("company") or "Nicht angegeben"
        result["Blog / Website"]    = r.get("blog") or "Nicht angegeben"
        result["Twitter"]           = r.get("twitter_username") or "Nicht angegeben"
        result["Öffentliche Repos"] = str(r.get("public_repos", 0))
        result["Follower"]          = str(r.get("followers", 0))
        result["Folgt"]             = str(r.get("following", 0))
        result["Account erstellt"]  = str(r.get("created_at", "?"))[:10]
        result["Letztes Update"]    = str(r.get("updated_at", "?"))[:10]
        result["GitHub Profil"]     = r.get("html_url", f"https://github.com/{username}")
    except Exception as e:
        result["Fehler"] = f"API-Fehler: {e}"
    try:
        repos_r = requests.get(
            f"https://api.github.com/users/{username}/repos?sort=updated&per_page=5",
            headers=headers, timeout=8
        ).json()
        if isinstance(repos_r, list):
            for i, repo in enumerate(repos_r[:5]):
                result[f"Repo {i+1}"] = f"{repo.get('name','?')} – ⭐{repo.get('stargazers_count',0)} – {repo.get('html_url','')}"
    except:
        pass
    try:
        events_r = requests.get(
            f"https://api.github.com/users/{username}/events/public?per_page=10",
            headers=headers, timeout=8
        ).json()
        emails_found = set()
        if isinstance(events_r, list):
            for event in events_r:
                if event.get("type") == "PushEvent":
                    commits = event.get("payload", {}).get("commits", [])
                    for commit in commits:
                        author = commit.get("author", {})
                        email = author.get("email", "")
                        if email and "noreply" not in email and email not in emails_found:
                            emails_found.add(email)
        if emails_found:
            for i, email in enumerate(list(emails_found)[:3]):
                result[f"E-Mail aus Commits {i+1}"] = email
    except:
        pass
    result["Commit-E-Mail Suche"] = f"https://github.com/{username}?tab=overview"
    result["Alle Repos"]          = f"https://github.com/{username}?tab=repositories"
    return result

def github_email_search(email: str) -> dict:
    result = {
        "GitHub Commit-Suche":  f"https://github.com/search?q={email}&type=commits",
        "GitHub Code-Suche":    f"https://github.com/search?q={email}&type=code",
        "GitLab-Suche":         f"https://gitlab.com/search?search={email}",
        "Google GitHub-Dork":   f"https://www.google.com/search?q=%22{email}%22+site%3Agithub.com",
    }
    return result
