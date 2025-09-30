import requests
import os
import regex as re
from dotenv import load_dotenv

# Load environment variables from a .env file if present
load_dotenv()

def get_issue_bugzilla(issue_id):
    """
    Fetch issue details from Bugzilla using the provided issue ID.  
    Note: issue_id should be a 7-digit number (e.g., '1234567')  
    """
    url = f"https://bugzilla.mozilla.org/rest/bug/{issue_id}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data["bugs"][0]["summary"]
    else:
        print(f"Error - Failed to make API call for issue tracking: {response.status_code} - {response.text}")


def get_issue_launchpad(issue_id):
    """
    Fetch issue details from Launchpad using the provided issue ID.
    Note: issue_id should start with '#' (e.g., '#1234567')
    """
    url = f"https://api.launchpad.net/devel/bugs/{issue_id[1:]}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data["description"]
    else:
        print(f"Error - Failed to make API call for issue tracking: {response.status_code} - {response.text}")


def get_issue_phabricator(issue_id):
    """
    Fetch issue details from Phabricator using the provided issue ID.
    Note: issue_id should start with 'T' (e.g., 'T12345')
    """
    url = "https://phabricator.wikimedia.org/api/maniphest.search"
    token = os.getenv("PHABRICATOR_TOKEN")
    headers = {
        "user-agent": "MyPhabBot/1.0"
    }
    payload = {
        "api.token": token,
        "constraints[ids][0]": int(issue_id[1:])
    }
    response = requests.post(url, headers=headers, data=payload)
    if response.status_code == 200:
        data = response.json()
        return data['result']['data'][0]['fields']['description']['raw']
    else:
        print(f"Error - Failed to make API call for issue tracking: {response.status_code} - {response.text}")


def get_issue(org_name, issue_id):
    """
    Fetch issue details based on the organization name and issue ID.
    """
    if org_name == "Mirantis":
        return get_issue_launchpad(issue_id)
    elif org_name == "mozilla":
        return get_issue_bugzilla(issue_id)
    elif org_name == "openstack":
        return get_issue_launchpad(issue_id)
    elif org_name == "wikimedia":
        return get_issue_phabricator(issue_id)
    else:
        return None

def get_issue_tags_mirantis(commit_message):
    """
    Extract issue tags from a commit message from a Mirantis repo.
    """
    pattern = r'#\d{7}\b'
    issue_tags = re.findall(pattern, commit_message)
    return list(set(issue_tags))[0] if issue_tags else None

def get_issue_tags_mozilla(commit_message):
    """
    Extract issue tags from a commit message from a Mozilla repo.
    """
    pattern = r'\d{7}\b'
    issue_tags = re.findall(pattern, commit_message)
    return list(set(issue_tags))[0] if issue_tags else None



def get_issue_tags_openstack(commit_message):
    """
    Extract issue tags from a commit message from a OpenStack repo.
    """
    pattern = r'#\d{7}\b'
    issue_tags = re.findall(pattern, commit_message)
    return list(set(issue_tags))[0] if issue_tags else None


def get_issue_tags_wikimedia(commit_message):
    """
    Extract issue tags from a commit message from a Wikimedia repo.
    """
    pattern = r'T\d{5,6}\b'
    issue_tags = re.findall(pattern, commit_message)
    return list(set(issue_tags))[0] if issue_tags else None


def get_issue_tags(org_name, commit_message):
    """ 
    Extract issue tags based on the organization name and commit message.
    """
    if org_name == "Mirantis":
        return get_issue_tags_mirantis(commit_message)
    elif org_name == "mozilla":
        return get_issue_tags_mozilla(commit_message)
    elif org_name == "openstack":
        return get_issue_tags_openstack(commit_message)
    elif org_name == "wikimedia":
        return get_issue_tags_wikimedia(commit_message)
    else:
        return None