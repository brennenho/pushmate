import subprocess

from rich.progress import Progress, SpinnerColumn, TextColumn


from pushmate.config import Config
from pushmate.git import GitTarget, get_diffs
from pushmate.messages import print_error, print_success, print_warning
from pushmate.llm_client import LLMClient


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
            progress.add_task(description="Generating commit message...", total=None)

            diff_output = get_diffs(GitTarget.COMMIT)

            if diff_output == "":
                return ""

            # Generate commit message using a LLM
            client = LLMClient()
            prompt = self.get_commit_prompt(diff_output, max_chars)
            response = client.prompt(prompt)

            if response != "":
                print_success("Commit message generated.")

            return response
