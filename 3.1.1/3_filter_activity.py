import csv
import subprocess
import tempfile
import shutil
from datetime import datetime
from collections import Counter
import time
import argparse

MIN_COMMITS_PER_MONTH = 2
MIN_ACTIVE_MONTHS = 12

def is_active_repo(clone_url, min_commits_per_month=MIN_COMMITS_PER_MONTH, min_active_months=MIN_ACTIVE_MONTHS, retry_on_auth=True):
    tmpdir = tempfile.mkdtemp()
    try:
        try:
            subprocess.run(
                ["git", "clone", "--bare", clone_url, tmpdir],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                check=True,
                text=True
            )
        except subprocess.CalledProcessError as e:
            stderr = e.stderr.lower()
            if "authentication" in stderr or "permission denied" in stderr:
                if retry_on_auth:
                    print(f"Authentication issue for {clone_url}. Waiting 10s before retry...")
                    time.sleep(10)
                    return is_active_repo(clone_url, min_commits_per_month, min_active_months, retry_on_auth=False)
                else:
                    print(f"Repeated authentication failure for {clone_url}")
                    return False
            else:
                print(f"Git error for {clone_url}: {e.stderr.strip()}")
                return False

        result = subprocess.run(
            ["git", "--git-dir", tmpdir, "log", "--pretty=format:%cI"],
            capture_output=True, text=True, check=True
        )
        
        dates = [datetime.fromisoformat(d.strip()).replace(tzinfo=None) for d in result.stdout.splitlines()]
        if not dates:
            print(f"No commits found for {clone_url}")
            return False

        counter = Counter((d.year, d.month) for d in dates)
        active_months = sum(1 for count in counter.values() if count >= min_commits_per_month)

        if active_months >= min_active_months:
            print(f"{clone_url} active ({active_months} months)")
            return True
        else:
            print(f"{clone_url} inactive ({active_months} months)")
            return False

    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Filter active repositories")
    parser.add_argument("--in", dest="input_csv", default="iac_repos.csv")
    parser.add_argument("--out", dest="output_csv", default="iac_repos_active.csv")
    args = parser.parse_args()
    
    with open(args.input_csv, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        repos = list(reader)

    active_repos = []
    for repo in repos:
        url = repo["clone_url"]
        name = repo["name"]
        if is_active_repo(url):
            active_repos.append(repo)

    with open(args.output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=reader.fieldnames)
        writer.writeheader()
        writer.writerows(active_repos)
    
    print(f"Filtered {len(active_repos)} active repos (≥{MIN_COMMITS_PER_MONTH} commits/month for at least {MIN_ACTIVE_MONTHS} months)")