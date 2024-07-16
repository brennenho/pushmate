import re
import subprocess

from enum import Enum

from pushmate.config import Config
from pushmate.messages import print_error, print_success, print_warning


class GitTarget(Enum):
    COMMIT = "commit"
    PR = "pr"


class RepoInfo:
    owner_name: str
    repo_name: str
    current_branch: str
    default_branch: str


def create_commit(message):
    """
    Creates a new commit with the given message.

    Args:
        message (str): The commit message.
    """
    try:
        subprocess.run(["git", "commit", "-m", message])
        print_success("Committed successfully.")
    except Exception as e:
        print_error()


def get_diffs(target: GitTarget, branch: str = "") -> str:
    """
    Retrieves the statistics of the changes made to the staged files in the git repository.

    Returns:
        A list of filenames of the staged files that have changes within the specified limit.
        Returns None if there are no changes staged to commit or if an error occurs.
    """
    try:
        config = Config()
        default_branch = get_repo_info().default_branch
        if target == GitTarget.COMMIT:
            diff_stat = subprocess.run(
                ["git", "diff", "--cached", "--stat"], capture_output=True, text=True
            )
        elif target == GitTarget.PR:
            diff_stat = subprocess.run(
                ["git", "diff", f"{default_branch}..{branch}", "--stat"],
                capture_output=True,
                text=True,
            )

        if "error: unknown option `cached'" in diff_stat.stderr:
            print_error(
                "Not a git repository. Please initialize a git repository and try again."
            )
            return None

        if diff_stat.returncode == 0:
            diff_output = diff_stat.stdout

            # Empty diff output means no changes staged to commit
            if not diff_output:
                print_error("No changes staged to commit.")
                return None
        else:
            return None

        files_within_limit = []
        max_changes = int(Config().get_option("max_changes"))

        # Parse diff output to get filenames and changes
        for line in diff_output.splitlines():
            parts = line.split("|")
            if len(parts) == 2:
                filename = parts[0].strip()
                changes = parts[1].strip().split()[0]
                if changes.isdigit() and int(changes) <= max_changes:
                    files_within_limit.append(filename)
                else:
                    print_warning(
                        f"File [bold]{filename}[/bold] has {changes} changes. Skipping file in LLM summary."
                    )

        diff_output = ""
        for file in files_within_limit:
            if target == GitTarget.COMMIT:
                diff = subprocess.run(
                    ["git", "diff", "--cached", file],
                    capture_output=True,
                    text=True,
                )
            elif target == GitTarget.PR:
                diff = subprocess.run(
                    ["git", "diff", f"{default_branch}..{branch}", "--", file],
                    capture_output=True,
                    text=True,
                )
            diff_output += diff.stdout

        return diff_output

    except Exception as e:
        if "No such file or directory: 'git'" in str(e):
            print_error("Git is not installed. Please install git and try again.")
        else:
            print_error()
        return None


def get_repo_info() -> RepoInfo:
    """
    Retrieves the repository information.

    Returns:
        A tuple containing the repository name, owner name, current branch, and default branch.
    """
    try:
        info = RepoInfo()
        # Get the repository URL
        repo_url = subprocess.run(
            ["git", "config", "--get", "remote.origin.url"],
            capture_output=True,
            text=True,
        ).stdout.strip()

        # Extract the owner and repository name from the URL
        match = re.search(r"github.com[:/](.+)/(.+?)(.git)?$", repo_url)
        if match:
            info.owner_name = match.group(1)
            info.repo_name = match.group(2)
        else:
            print_error("Unable to parse repository URL.")

        # Get the current branch name
        info.current_branch = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"], capture_output=True, text=True
        ).stdout.strip()

        # Get the default branch name
        info.default_branch = subprocess.run(
            ["git", "remote", "show", "origin"], capture_output=True, text=True
        ).stdout
        info.default_branch = re.search(
            r"HEAD branch: (.+)", info.default_branch
        ).group(1)

        return info
    except Exception as e:
        print(f"Error: {e}")
        return None, None, None, None
