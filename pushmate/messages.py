from rich import print


def print_error(message: str = "an unexpected error occurred"):
    print(f"[bold red]ERROR[/bold red] | {message}")


def print_success(message):
    print(f"[bold green]SUCCESS[/bold green]| {message}")


def print_warning(message: str = "Warning!"):
    print(f"[bold yellow]WARNING[/bold yellow] | {message}")


def print_abort(message: str = ""):
    print(f"[bold red]ABORT[/bold red] | {message}")


def print_info(message: str):
    print(f"[bold blue]INFO[/bold blue] | {message}")
