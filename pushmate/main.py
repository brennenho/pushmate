import typer

from rich import print
from rich.markdown import Markdown
from rich.prompt import Prompt
from typing import Annotated, Optional

from pushmate.commits import Commits
from pushmate.config import Config
from pushmate.git import create_commit
from pushmate.github import create_pr
from pushmate.pull_requests import PullRequests

app = typer.Typer(no_args_is_help=True, rich_markup_mode="rich")


@app.callback()
def callback():
    """
    A CLI utilizing LLMs for git commits and PRs
    """


@app.command()
def test():
    """
    Test command
    """
    typer.echo("Test command ran")


@app.command()
def commit(
    max_chars: Annotated[
        int,
        typer.Option(
            help="Override default # of max characters for the commit message.",
            show_default=False,
        ),
    ] = 0,
):
    """
    Generate a commit message
    """
    commits = Commits()
    message = None
    while not message:
        message = commits.get_commit_message(max_chars)
        if message == "":
            raise typer.Exit()

        print(f":bookmark: | [bold blue]Message:[/bold blue]")
        print(Markdown(f"```md\n{message}\n```"))
        confirmation = Prompt.ask(
            ":question: | [bold]Create commit with this message?[/bold]",
            choices=["y", "n", "regen"],
        )

        if confirmation.lower() == "n":
            print(":x: | [bold red]Commit aborted[/bold red]")
            raise typer.Exit()
        elif confirmation.lower() == "regen":
            message = None

    create_commit(message)


@app.command()
def pr():
    """
    Generate a pull request
    """
    prs = PullRequests()
    message = None
    while not message:
        message = prs.get_pr_message()
        if not message:
            raise typer.Exit()

        print(f":bookmark: | [bold blue]Message:[/bold blue]")
        print(Markdown(f"```md\n{message}\n```"))
        confirmation = Prompt.ask(
            ":question: | [bold]Create pull request with this message?[/bold]",
            choices=["y", "n", "regen"],
        )

        if confirmation.lower() == "n":
            print(":x: | [bold red]Pull request aborted[/bold red]")
            raise typer.Exit()
        elif confirmation.lower() == "regen":
            message = None

    create_pr(message)


@app.command()
def config(
    value: Annotated[
        Optional[str],
        typer.Argument(
            help="If provided, will be set as config value. Leave blank to view the current value.",
            show_default=False,
        ),
    ] = None,
    provider: Annotated[
        bool,
        typer.Option(
            help="The LLM provider to use",
            show_default=False,
            rich_help_panel="Configuration",
        ),
    ] = False,
    max_changes: Annotated[
        bool,
        typer.Option(
            help="Maximum # of changes per file. Files with more changes will not be summarized. (Default: 500)",
            show_default=False,
            rich_help_panel="Configuration",
        ),
    ] = False,
    max_chars: Annotated[
        bool,
        typer.Option(
            help="Maximum # of characters the commit message should be (Default: 80)",
            show_default=False,
            rich_help_panel="Configuration",
        ),
    ] = False,
    github_token: Annotated[
        bool,
        typer.Option(
            help="GitHub token to use for PRs",
            show_default=False,
            rich_help_panel="Configuration",
        ),
    ] = False,
    openai: Annotated[
        bool,
        typer.Option(
            help="OpenAI API Key", show_default=False, rich_help_panel="Configuration"
        ),
    ] = False,
):
    """
    View and set configuration options
    """
    config = Config()

    options = {k: v for k, v in locals().items() if v is True}
    if not options:
        config.read_config()
        print(f"Configuration: {config.get_options()}")
        return

    if len(options) > 1:
        print("Please provide only one option at a time")
        return

    option = list(options.keys())[0]
    if value:
        config.set_option(option, value)
        print(f"{option} set to {value}")
    else:
        print(f"{option}: {config.get_option(option)}")

    print(f"Configuration: {config.get_options()}")
