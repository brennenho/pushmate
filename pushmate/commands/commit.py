import typer

from rich import print
from rich.console import Console
from rich.markdown import Markdown
from rich.prompt import Prompt

from pushmate.commands.config import Config
from pushmate.clients.git import GitClient, GitTarget
from pushmate.clients.llm_client import LLMClient
from pushmate.utils.messages import (
    get_prompt,
    get_status,
    print_abort,
    print_error,
    print_success,
)

console = Console()


def run_commit(max_chars: int):

    git_client = GitClient(GitTarget.COMMIT)
    with console.status(get_status("retrieving changed files")):
        invalid_files = git_client.get_diff_files()

    if not git_client.valid_files:
        raise typer.Exit()

    for filename, changes in invalid_files:
        confirmation = Prompt.ask(
            get_prompt(
                f"file {filename} has {changes} changes: include in commit message?"
            ),
            choices=["y", "N"],
            default="N",
        )
        if confirmation.lower() == "y":
            git_client.valid_files.append(filename)

    with console.status(get_status("analyzing changed files")):
        diff_output = git_client.get_diffs()

    # For some reason printing this within the status context manager causes the spinner to hang
    if diff_output:
        print_success("changed files analyzed")
    else:
        print_error("could not analyze changed files")
        raise typer.Exit()

    llm_client = LLMClient()
    generation = "generating"
    message = None
    while not message:
        with console.status(get_status(f"{generation} commit message")):
            prompt = get_commit_prompt(diff_output, max_chars)
            message = llm_client.prompt(prompt)

        if message:
            print_success("commit message generated")
        else:
            print_error("unable to generate commit message")
            raise typer.Exit()

        print(Markdown(f"```md\n{message}\n```"))
        confirmation = Prompt.ask(
            get_prompt("generate a commit with this message?"),
            choices=["Y", "n", "regen"],
            default="Y",
        )

        if confirmation.lower() == "n":
            print_abort("commit aborted")
            raise typer.Exit()

        elif confirmation.lower() == "regen":
            message = None
            generation = "regenerating"

    with console.status(get_status("creating commit")):
        commit_created = git_client.create_commit(message)

    if commit_created:
        print_success("commit created")
    else:
        print_error()
        raise typer.Exit()


def get_commit_prompt(diff_output: str, max_chars) -> list[dict[str, str]]:
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
