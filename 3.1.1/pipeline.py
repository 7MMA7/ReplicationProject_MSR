import subprocess
import sys
from urllib.parse import urlparse

def run_script(script_name, args=None):
    cmd = ["python", script_name]
    if args:
        cmd.extend(args)
    
    try:
        subprocess.run(cmd, check=True)
        print(f"{script_name} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error in {script_name}: {e}")
        return False

def get_org_name_from_url(url):
    path_parts = urlparse(url).path.strip("/").split("/")
    return path_parts[0] if path_parts else "org"

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python pipeline.py <GitHub user/org URL>")
        sys.exit(1)
    
    github_url = sys.argv[1]
    org_name = get_org_name_from_url(github_url)
    
    repos_csv = f"3.1.1/downloadable/repos_{org_name}.csv"
    iac_csv = f"3.1.1/iac_filter/iac_repos_{org_name}.csv"
    iac_active_csv = f"3.1.1/activity/iac_repos_active_{org_name}.csv"
    final_csv = f"3.1.1/final/defects_{org_name}.csv"
    
    scripts = [
        ("3.1.1/1_check_repos.py", [github_url, "--out", repos_csv]),
        ("3.1.1/2_filter_iac.py", ["--in", repos_csv, "--out", iac_csv]),
        ("3.1.1/3_filter_activity.py", ["--in", iac_csv, "--out", iac_active_csv]),
        ("3.1.1/4_analyze_iac.py", ["--in", iac_active_csv, "--out", final_csv, "--org", org_name])
    ]
    
    print("Starting the GitHub repos processing pipeline")
    print(f"Target URL: {github_url}")
    print("-" * 50)
    
    for script_name, args in scripts:
        print(f"Running {script_name}...")
        if not run_script(script_name, args):
            print(f"Stopping the pipeline due to error in {script_name}")
            sys.exit(1)
        print()
    
    print("Pipeline completed")
