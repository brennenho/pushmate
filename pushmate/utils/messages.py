from rich.console import Console

console = Console()


def print_error(message: str = "an unexpected error occurred"):
    console.print(f":collision: [red]{message}[/red]")


def print_success(message):
    console.print(f":heavy_check_mark: [green]{message}[/green]")


def print_abort(message: str = ""):
    console.print(f":heavy_exclamation_mark: [red]{message}[/red]")


def print_info(message: str):
    console.print(f"[bold blue]INFO[/bold blue] | {message}")


def get_prompt(message: str):
    return f":speech_balloon: [yellow]{message}[/yellow]"


def get_status(message: str):
    return f"[yellow]{message}[/yellow] \n"
