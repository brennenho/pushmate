from rich.console import Console

console = Console()


def print_error(message: str = "an unexpected error occurred"):
    console.print(f"[bold red]ERROR[/bold red] | {message}")


def print_success(message):
    console.print(f":heavy_check_mark: [green]{message}[/green]")


def print_warning(message: str = "Warning!"):
    console.print(f"[bold yellow]WARNING[/bold yellow] | {message}")


def print_abort(message: str = ""):
    console.print(f"[bold red]ABORT[/bold red] | {message}")


def print_info(message: str):
    console.print(f"[bold blue]INFO[/bold blue] | {message}")


def get_prompt(message: str):
    return f"[bold yellow]PROMPT[/bold yellow] | {message}"


def get_status(message: str):
    return f"[yellow]{message}[/yellow] \n"
