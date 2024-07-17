import typer

from rich import print
from rich.console import Console
from rich.markdown import Markdown
from rich.prompt import Prompt

from pushmate.clients.git import GitClient, GitTarget
from pushmate.clients.github import create_pr
from pushmate.clients.llm_client import LLMClient
from pushmate.utils.messages import (
    get_prompt,
    get_status,
    print_abort,
    print_error,
    print_success,
)

console = Console()


def run_pr(branch: str):
    git_client = GitClient(GitTarget.PR)
    with console.status(get_status("retrieving changed files")):
        invalid_files = git_client.get_diff_files(branch)

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
        diff_output = git_client.get_diffs(branch)

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
        with console.status(get_status(f"{generation} pull request message")):
            prompt = get_pr_prompt(diff_output)
            message = llm_client.prompt(prompt)

        if message:
            print_success("pull request message generated")
        else:
            print_error("unable to generate pull request message")
            raise typer.Exit()

        print(Markdown(f"```md\n{message}\n```"))
        confirmation = Prompt.ask(
            get_prompt("generate a pull request with this message?"),
            choices=["Y", "n", "regen"],
            default="Y",
        )

        if confirmation.lower() == "n":
            print_abort("commit aborted")
            raise typer.Exit()

        elif confirmation.lower() == "regen":
            message = None
            generation = "regenerating"

    push_status = GitClient.push_changes()

    if push_status:
        print_success("pushed committed changes")
    else:
        print_error("could not push committed changes")
        raise typer.Exit()

    with console.status(get_status("creating pull request")):
        pr_link = create_pr(branch, message)

    if pr_link == "422":
        print_error(
            "validation failed: both branches must exist on github and cannot already have a pull request"
        )
        raise typer.Exit()
    elif pr_link:
        print_success("pull request created")
        typer.launch(pr_link)
    else:
        print_error()
        raise typer.Exit()


def get_pr_prompt(diff_output: str):
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
