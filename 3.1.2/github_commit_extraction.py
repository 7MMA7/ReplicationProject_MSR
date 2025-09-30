import pandas as pd
import sys
from pathlib import Path
module_path = Path(__file__).resolve().parent.parent / "3.1.1"
sys.path.append(str(module_path))
from github_api_manager import github_api

def repo_commits_extraction(org_url, repo_name):

    print(f"Processing repository: {repo_name}")

    # Repositories identification
    url_repo_commits = f"{org_url}{repo_name}/commits"

    # GitHub API Call
    data = github_api.make_request(url_repo_commits)

    # Checking request success
    if data:

        # Commit messages and SHAs extraction
        commits_messages = []
        commits_shas = []
        for commit in data:
            commits_messages.append(f"{commit['commit']['message'].strip()}")
            commits_shas.append(f"{commit['sha']}")

        commits_df = pd.DataFrame(columns=['repo_name', 'commit_message', 'commit_sha'])
        for message, sha in zip(commits_messages, commits_shas):
            commits_df.loc[len(commits_df)] = [repo_name, message, sha]

        return commits_df

def files_from_commit_extraction(org_url, repo_name, commit_sha):
    
    # Commits identification
    url_repo_commits = f"{org_url}{repo_name}/commits/{commit_sha}"

    # GiHub API Call
    data = github_api.make_request(url_repo_commits)

    # Checking request success
    if data:

        # File names extraction from commit
        files_from_commit_df = pd.DataFrame(columns=['file_name'])
        for file in data["files"]:
            # We assume that IAC files are only .pp files (based on previous analysis)
            if ".pp" in file['filename']:
                files_from_commit_df.loc[len(files_from_commit_df)] = [file['filename'].strip()]

        return files_from_commit_df
    
