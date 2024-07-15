from rich.progress import Progress, SpinnerColumn, TextColumn


class PullRequests:

    def get_pr_prompt(self, diff_output: str):
        """
        Generate a pull request prompt based on the given diff output.
        """
        return [
            {
                "role": "system",
                "content": f"""
                            You are a helpful agent that evaluates changes in repository branches and summarizes them into a pull request. 
                            Given a list of changes, fill out the following pull request template with the necessary information. 
                            Instructions for each section are between the '<>' brackets. 
                            You can use markdown to format your message.
                            Prioritize the most important changes and keep the message as concise as possible.
                            Only return the filled-out pull request template with no additional information.

                            Title: <concise pull request title summarizing key changes>
                            <1-3 sentence summary of the pull request, highlighting major changes concisely>

                            ### Key Changes:
                            - <bulleted list of major changes, skipping minor changes or changes from dependencies>

                            ### Further Improvements:
                            - <a short list of potential future improvements>
                            """,
            },
            {
                "role": "user",
                "content": f"""
                            {diff_output}
                            """,
            },
        ]

    def get_pr(self) -> str:
        """
        Generate a pull request based on the changes made in the current branch.

        Returns:
            str: The generated pull request
        """
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            pass
