import requests

from pushmate.config import Config
from pushmate.git import get_repo_info
from pushmate.utils import parse_pr


headers = {
    "Authorization": f"token {Config().get_option('github_token')}",
    "Accept": "application/vnd.github.v3+json",
    "X-GitHub-Api-Version": "2022-11-28",
}


def create_pr(message: str):
    """
    Creates a new pull request with the given message.

    Args:
        message (str): The pull request message.
    """
    title, body = parse_pr(message)
    info = get_repo_info()
    url = f"https://api.github.com/repos/{info.owner_name}/{info.repo_name}/pulls"
    data = {
        "title": title,
        "body": body,
        "head": info.current_branch,
        "base": info.default_branch,
    }

    response = requests.post(url=url, headers=headers, json=data)
