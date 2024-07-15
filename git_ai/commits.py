import subprocess

from rich.progress import Progress, SpinnerColumn, TextColumn


from git_ai.config import Config
from git_ai.messages import print_error, print_success, print_warning
from git_ai.llm_client import LLMClient


class Commits:

    def get_commit_prompt(self, diff_output: str, max_chars) -> list[dict[str, str]]:
        """
        Generates a commit prompt based on the given diff output.

        Args:
            diff_output (str): The diff output containing the list of changes.

        Returns:
            list: A list of dictionaries representing the commit prompt. Each dictionary has two keys:
                - 'role': The role of the message (either 'system' or 'user').
                - 'content': The content of the message.
        """

        if max_chars == 0:
            max_chars = Config().get_option("max_chars")

        return [
            {
                "role": "system",
                "content": f"""
                            You are a helpful agent that evaluates changes in repositories and summarizes them into a git commit message. 
                            Given a list of changes, summarize all changes into a single, concise commit message that is no more than {max_chars} characters.
                            Ignore minor changes if needed to keep the message concise and within the character limit. 
                            Only output the single git commit message.
                            """,
            },
            {
                "role": "user",
                "content": f"""
                            {diff_output}
                            """,
            },
        ]

    def get_commit_message(self, max_chars: int) -> str:
        """
        Retrieves the commit message for the changes made in the current branch.

        Returns:
            str: The generated commit message.
        """
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            diff_output = ""
            try:
                progress.add_task(
                    description="Generating commit message...", total=None
                )

                # Check diff stats for staged files
                files = self.get_diff_stats()
                if not files:
                    return ""

                # Get diff for each valid staged file
                for file in files:
                    diff = subprocess.run(
                        ["git", "diff", "--cached", file],
                        capture_output=True,
                        text=True,
                    )
                    diff_output += diff.stdout

            except Exception as e:
                print_error()
                return ""

            if diff_output == "":
                return ""

            # Generate commit message using a LLM
            client = LLMClient()
            prompt = self.get_commit_prompt(diff_output, max_chars)
            response = client.prompt(prompt)

            if response != "":
                print_success("Commit message generated.")

            return response

    def get_diff_stats(self):
        """
        Retrieves the statistics of the changes made to the staged files in the git repository.

        Returns:
            A list of filenames of the staged files that have changes within the specified limit.
            Returns None if there are no changes staged to commit or if an error occurs.
        """
        try:
            # Get diff stats for staged files
            diff_stat = subprocess.run(
                ["git", "diff", "--cached", "--stat"], capture_output=True, text=True
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

            return files_within_limit

        except Exception as e:
            if "No such file or directory: 'git'" in str(e):
                print_error("Git is not installed. Please install git and try again.")
            else:
                print_error()
            return None

    def create_commit(self, message):
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
