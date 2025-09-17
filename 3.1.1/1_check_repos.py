import subprocess
import sys
import csv
from urllib.parse import urlparse
from github_api_manager import github_api

def get_repos(user_or_org):
    path = urlparse(user_or_org).path.strip("/")
    url = f"https://api.github.com/users/{path}/repos"
    repos = []
    page = 1
    
    while True:
        data = github_api.make_request(url, params={"per_page": 100, "page": page})
        if not data or "message" in data:
            break
        repos.extend(data)
        page += 1
    
    return repos

def check_clonable(clone_url):
    try:
        subprocess.run(
            ["git", "ls-remote", clone_url],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )
        return True
    except subprocess.CalledProcessError:
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python 1_check_repos.py <GitHub user/org URL> --out [output CSV filename]")
        sys.exit(1)
    
    url = sys.argv[1]
    output_csv = sys.argv[3] if len(sys.argv) >= 3 else "repos.csv"
    
    repos = get_repos(url)
    
    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["name", "clone_url"])
        
        for repo in repos:
            name = repo["name"]
            clone_url = repo["clone_url"]
            clonable = check_clonable(clone_url)
            
            if clonable:
                writer.writerow([name, clone_url])
            
            status = "clonable" if clonable else "not clonable"
            print(f"{name}: {status}")