import typer

from rich.console import Console
from rich.table import Table
from typing import Annotated, Optional

from pushmate.commands.commit import run_commit
from pushmate.commands.issue import run_issue
from pushmate.commands.pr import run_pr
from pushmate.commands.config import Config
from pushmate.utils.messages import (
    print_abort,
    print_info,
    print_info,
    print_success,
)

app = typer.Typer(no_args_is_help=True, rich_markup_mode="rich")
console = Console()


@app.callback()
def callback():
    """
    PushMate: automate your git workflow with AI.
    """


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
    Automatically generate a git commit based on the currently staged changes.
    """
    run_commit(max_chars)


@app.command()
def pr(
    branch: Annotated[
        str,
        typer.Option(
            help="The branch to pull request against. Leave blank to use the default branch.",
            show_default=False,
            rich_help_panel="Configuration",
        ),
    ] = "",
):
    """
    Automatically generate a GitHub pull request based on the currently branch's HEAD.
    """
    run_pr(branch)


@app.command()
def issue():
    """
    Automatically generate a GitHub issue based on user prompts.
    """
    run_issue()


@app.command()
def config(
    value: Annotated[
        Optional[str],
        typer.Argument(
            help="The value to set an option to. Leave blank to view the current value.",
            show_default=False,
        ),
    ] = None,
    provider: Annotated[
        bool,
        typer.Option(
            help="Provider to use for LLM calls.",
            show_default=False,
            rich_help_panel="Configuration",
        ),
    ] = False,
    max_changes: Annotated[
        bool,
        typer.Option(
            help="Maximum # of changes to automatically include in a commit message. Files with more changes will be prompted for inclusion. (Default: 500)",
            show_default=False,
            rich_help_panel="Configuration",
        ),
    ] = False,
    max_chars: Annotated[
        bool,
        typer.Option(
            help="Maximum # of characters for a commit message. (Default: 50)",
            show_default=False,
            rich_help_panel="Configuration",
        ),
    ] = False,
    github_token: Annotated[
        bool,
        typer.Option(
            help="GitHub API Token.",
            show_default=False,
            rich_help_panel="Configuration",
        ),
    ] = False,
    openai: Annotated[
        bool,
        typer.Option(
            help="OpenAI API Key.", show_default=False, rich_help_panel="Configuration"
        ),
    ] = False,
):
    """
    Set or view PushMate configuration options.
    """
    config = Config()
    options = {k: v for k, v in locals().items() if v is True}

    # No options provided, print current configuration
    if not options:
        if value:
            print_abort("please provide an option to access")
        else:
            config.read_config()
            table = Table(
                "option",
                "value",
                title="current configuration options",
                caption=r"update an option with [bold]pm config --\[option] \[value][/bold]",
            )
            for k, v in config.get_options().items():
                table.add_row(k.replace("_", "-"), v)

            console.rule(style="blue")
            console.print(table)
            console.rule(style="blue")
        raise typer.Exit()

    if len(options) > 1:
        print_abort("only one option can be accessed at a time")
        raise typer.Exit()

    option = list(options.keys())[0]
    if value:
        config.set_option(option, value)
        print_success(f"set [bold]{option}[/bold] to [bold]{value}[/bold]")
    else:
        print_info(f"[bold]{option}[/bold] is set to: {config.get_option(option)}")
