import subprocess

from rich import print
from rich.progress import Progress, SpinnerColumn, TextColumn


from git_ai.messages import print_error, print_success, print_warning
from git_ai.llm_client import LLMClient


class Commits:

    def get_commit_prompt(self, diff_output: str):
        return [
            {
                "role": "system",
                "content": """
                            You are a helpful agent that evaluates changes in repositories and summarizes them into a git commit message. 
                            Given a list of changes, summarize all changes into a single, concise commit message that is no more than 100 characters.
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

    def get_commit_message(self) -> str:
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
                files = self.get_diff_stats(500)
                if not files:
                    return ""

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

            client = LLMClient()
            prompt = self.get_commit_prompt(diff_output)
            response = client.prompt(prompt)

            if response != "":
                print_success("Commit message generated.")
            return response

    def get_diff_stats(self, max_changes: int):
        try:
            diff_stat = subprocess.run(
                ["git", "diff", "--cached", "--stat"], capture_output=True, text=True
            )

            if "error: unknown option `cached'" in diff_stat.stderr:
                print_error(
                    "Not a git repository. Please initialize a git repository and try again."
                )
                return ""

            if diff_stat.returncode == 0:
                diff_output = diff_stat.stdout
                if not diff_output:
                    print_error("No changes staged to commit.")
                    return None
            else:
                return None

            # Process the diff statistics to filter files
            files_within_limit = []
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
        try:
            subprocess.run(["git", "commit", "-m", message])
            print_success("Committed successfully.")
        except Exception as e:
            print(e)
            print_error()
