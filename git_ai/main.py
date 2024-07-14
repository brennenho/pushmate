import typer


app = typer.Typer(no_args_is_help=True)


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
