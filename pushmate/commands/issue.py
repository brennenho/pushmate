import inquirer
import typer

from rich import print
from rich.console import Console
from rich.markdown import Markdown
from rich.prompt import Prompt

from pushmate.clients.git import GitClient
from pushmate.clients.github import create_issue
from pushmate.clients.llm_client import LLMClient
from pushmate.utils.editor import edit_text
from pushmate.utils.messages import (
    get_prompt,
    get_status,
    print_abort,
    print_error,
    print_success,
)


console = Console()


def run_issue():
    title = Prompt.ask(get_prompt("issue title"))
    body = Prompt.ask(get_prompt("issue description"))
    labels = Prompt.ask(get_prompt("issue labels (comma-separated)"))
    assignees = Prompt.ask(get_prompt("issue assignees (comma-separated)"))
    summarize = Prompt.ask(
        get_prompt("summarize issue with AI"), choices=["Y", "n"], default="Y"
    )

    if summarize.lower() == "y":
        llm_client = LLMClient()
        status = "summarizing"
        conversation = get_issue_prompt(title, body)
        summary = None
        while not summary:
            with console.status(get_status(f"{status} issue summary")):
                summary = llm_client.prompt(conversation)

            if summary:
                print_success("issue summary generated")
            else:
                print_error("unable to generate issue summary")
                raise typer.Exit()

            print(Markdown(f"```md\n{summary}\n```"))
            confirmation = inquirer.prompt(
                [
                    inquirer.List(
                        "action",
                        message="create an issue?",
                        choices=[
                            "create issue",
                            "edit issue summary",
                            "instruct llm on improvements",
                            "regenerate issue summary",
                            "abort",
                        ],
                    ),
                ]
            )["action"]

            if confirmation.lower() == "abort":
                print_abort("issue aborted")
                raise typer.Exit()

            elif confirmation.lower() == "regenerate issue summary":
                conversation.append(
                    {
                        "role": "user",
                        "content": "Edit this issue description for clarity and concision.",
                    }
                )
                summary = None
                status = "regenerating"

            elif confirmation.lower() == "instruct llm on improvements":
                feedback = Prompt.ask(get_prompt("feedback"))
                conversation.append({"role": "user", "content": feedback})
                summary = None
                status = "regenerating with feedback"

            elif confirmation.lower() == "edit commit message":
                summary = edit_text(summary)

        body = summary

    with console.status(get_status("creating issue")):
        assignees = [assignee.strip() for assignee in assignees.split(",")]
        labels = [label.strip() for label in labels.split(",")]
        issue_link = create_issue(title, body, labels, assignees)

    if issue_link == "422":
        print_error(
            "validation failed: both branches must exist on github and cannot already have a pull request"
        )
        raise typer.Exit()
    elif issue_link:
        print_success("issue created")
        typer.launch(issue_link)
    else:
        print_error()
        raise typer.Exit()


def get_issue_prompt(title: str, body: str) -> list[dict]:
    return [
        {
            "role": "system",
            "content": "You are a helpful assistant that aids developers in creating GitHub issues. Given the following issue title and description, rewrite the description in a more concise and informative manner. Only return the description of the issue as a single string. Do not include 'Description' in the response.",
        },
        {
            "role": "user",
            "content": f"Title: {title} \n\nDescription: {body}",
        },
    ]
