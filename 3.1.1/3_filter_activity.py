import csv
import subprocess
import tempfile
import shutil
from datetime import datetime, timedelta
from collections import Counter
import time
import argparse

MIN_COMMITS_PER_MONTH = 2

def is_active_repo(clone_url, min_commits_per_month=MIN_COMMITS_PER_MONTH, retry_on_auth=True):
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
                    return is_active_repo(clone_url, min_commits_per_month, retry_on_auth=False)
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
        
        first_commit = min(dates)
        current = datetime(first_commit.year + (first_commit.month // 12), (first_commit.month % 12) + 1, 1)
        last_commit = max(dates)
        last = last_commit.replace(day=1) - timedelta(days=1)
        
        while current <= last:
            if counter.get((current.year, current.month), 0) < min_commits_per_month:
                print(f"{clone_url} inactive in {current.year}-{current.month}")
                return False
            
            if current.month == 12:
                current = datetime(current.year + 1, 1, 1)
            else:
                current = datetime(current.year, current.month + 1, 1)
        
        return True
    
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Filter active repositories")
    parser.add_argument("--in", dest="input_csv", default="iac_repos.csv",
                        help="Input CSV filename (default: iac_repos.csv)")
    parser.add_argument("--out", dest="output_csv", default="iac_repos_active.csv",
                        help="Output CSV filename (default: iac_repos_active.csv)")
    
    args = parser.parse_args()
    
    input_csv = args.input_csv
    output_csv = args.output_csv

    with open(input_csv, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        repos = list(reader)

    active_repos = []
    for repo in repos:
        url = repo["clone_url"]
        name = repo["name"]
        
        if is_active_repo(url):
            active_repos.append(repo)
            print(f"{name}: active")
        else:
            print(f"{name}: inactive")

    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=reader.fieldnames)
        writer.writeheader()
        writer.writerows(active_repos)
    
    print(f"Filtered {len(active_repos)} active repos (≥{MIN_COMMITS_PER_MONTH} commits/month for all months)")