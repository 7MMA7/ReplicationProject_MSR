import os
import csv
import subprocess
import tempfile
import shutil
import time
import argparse

IAC_EXTENSIONS = {".pp"}

def count_iac_files(repo_path):
    total_files = 0
    iac_files = 0
    
    for root, _, files in os.walk(repo_path):
        for f in files:
            total_files += 1
            _, ext = os.path.splitext(f)
            full_path = os.path.join(root, f)
            
            if ext.lower() == ".pp":
                iac_files += 1
    
    return total_files, iac_files

def process_repo(clone_url, retries=2):
    tmpdir = tempfile.mkdtemp()
    try:
        attempt = 0
        while attempt < retries:
            try:
                subprocess.run(
                    ["git", "config", "--global", "http.postBuffer", "524288000"],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                    check=True, text=True
                )

                subprocess.run(
                    ["git", "init", "-b", "main"],
                    cwd=tmpdir,
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                    check=True, text=True
                )

                subprocess.run(
                    ["git", "remote", "add", "origin", clone_url],
                    cwd=tmpdir,
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                    check=True, text=True
                )

                subprocess.run(
                    ["git", "config", "core.sparseCheckout", "true"],
                    cwd=tmpdir,
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                    check=True, text=True
                )

                sparse_file = os.path.join(tmpdir, ".git", "info", "sparse-checkout")
                with open(sparse_file, "w") as f:
                    f.write("*.pp\n")

                subprocess.run(
                    ["git", "pull", "--depth=1", "origin", "HEAD"],
                    cwd=tmpdir,
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                    check=True, text=True
                )
                break

            except subprocess.CalledProcessError:
                attempt += 1
                time.sleep(5)
                if attempt == retries:
                    return 0, 0, 0
        
        total, iac = count_iac_files(tmpdir)
        ratio = (iac / total * 100) if total > 0 else 0
        return total, iac, ratio
    
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Filter IaC repositories")
    parser.add_argument("--in", dest="input_csv", default="repos.csv",
                        help="Input CSV filename (default: repos.csv)")
    parser.add_argument("--out", dest="output_csv", default="iac_repos.csv",
                        help="Output CSV filename (default: iac_repos.csv)")
    
    args = parser.parse_args()
    
    input_csv = args.input_csv
    output_csv = args.output_csv
    
    with open(input_csv, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        repos = list(reader)
    
    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["name", "clone_url"])
        
        for repo in repos:
            name = repo["name"]
            url = repo["clone_url"]
            total, iac, ratio = process_repo(url)
            keep = ratio >= 11
            
            if keep:
                writer.writerow([name, url])
            
            print(f"{name}: {iac}/{total} IaC files ({round(ratio, 2)}%) -> {'keep' if keep else 'discard'}")