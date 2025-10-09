import pandas as pd
from dotenv import load_dotenv
import os

# Implemented functions
from github_commit_extraction import repo_commits_extraction, files_from_commit_extraction
from tracker_issue_mining import get_issue_tags, get_issue

# Load environment variables from a .env file if present
load_dotenv()

def xcm_gnerator():
   """
   Generate the extended commit messages (XCM) linking IaC files commit messages to issues summary.
   """
   # Loading source and preparing results dataframe
   source_repo_df = pd.read_csv("3.1.2/results/IaC_repos.csv")
   result_df = pd.DataFrame(columns = ['org_name', 'repo_name', 'file_name', 'commit_message', 'commit_sha', 'issue_id', 'summary_issue', 'XCM'])

   # Configuration for API calls
   base_url = "https://api.github.com/repos/"
   org_names = ["Mirantis", "mozilla", "openstack", "wikimedia"]

   for org_name in org_names:
      # Iterate through each repository in the current organization
      print(f"Processing organization: {org_name}")
      org_url = f"{base_url}{org_name}/"

      for repo_name in source_repo_df[f'{org_name}']:
         if not pd.isna(repo_name):

            #Call the function to extract commits for the current repository
            repo_commits = repo_commits_extraction(org_url, repo_name)
            
            if repo_commits is not None:
               for _, row in repo_commits.iterrows():
                    commit_message = row['commit_message']
                    commit_sha = row['commit_sha']
    
                    #Call the function to extract IaC files from the current commit
                    files_from_commit = files_from_commit_extraction(org_url, repo_name, commit_sha)
    

                    for _, file_row in files_from_commit.iterrows():
                        file_name = file_row['file_name']

                        #Extract issue tags from the commit message
                        issue_id = get_issue_tags(org_name, commit_message)

                        #Fetch issue summary if an issue ID was found
                        summary_issue = get_issue(org_name, issue_id) if issue_id else None

                        #Construct the XCM
                        xcm = f"{file_name} | {commit_message} | {issue_id if issue_id else 'No Issue'} | {summary_issue if summary_issue else 'No Summary'}"

                        #Append the result to the dataframe
                        result_df.loc[len(result_df)] = [org_name, repo_name, file_name, commit_message, commit_sha, issue_id, summary_issue, xcm]
   result_df.to_csv("3.1.2/results/XCM_list.csv")

if __name__ == "__main__":
    xcm_gnerator()