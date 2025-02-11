import requests

from pushmate.commands.config import Config
from pushmate.clients.git import GitClient
from pushmate.utils.utils import parse_pr


headers = {
    "Authorization": f"token {Config().get_option('github_token')}",
    "Accept": "application/vnd.github.v3+json",
    "X-GitHub-Api-Version": "2022-11-28",
}


def create_pr(branch: str, message: str) -> str:
    """
    Creates a new pull request with the given message.

    Args:
        branch (str): The branch to merge into.
        message (str): The pull request message.
    """
    try:
        title, body = parse_pr(message)
        info = GitClient.get_repo_info()
        if not branch:
            branch = info.default_branch

        url = f"https://api.github.com/repos/{info.owner_name}/{info.repo_name}/pulls"
        data = {
            "title": title,
            "body": body,
            "head": info.current_branch,
            "base": branch,
        }

        response = requests.post(url=url, headers=headers, json=data)

        if response.status_code == 201:
            return response.json()["html_url"]
        elif response.status_code == 422:
            return "422"

        return None
    except Exception as e:
        return None


def create_issue(
    title: str, body: str, labels: list[str] = [], assignees: list[str] = []
):
    """
    Creates a new issue with the given title and body.

    Args:
        title (str): The issue title.
        body (str): The issue body.
        labels (list): A list of labels to assign to the issue.
        assignees (list): A list of assignees for the issue.
    """
    try:
        info = GitClient.get_repo_info()
        url = f"https://api.github.com/repos/{info.owner_name}/{info.repo_name}/issues"
        data = {
            "title": title,
            "body": body,
            "labels": labels,
            "assignees": assignees,
        }

        response = requests.post(url=url, headers=headers, json=data)

        if response.status_code == 201:
            return response.json()["html_url"]
        elif response.status_code == 422:
            return "422"

        return None
    except Exception as e:
        return None
