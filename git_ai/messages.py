from rich import print


def print_error(message: str = "Un unexpected error occurred."):
    print(f":collision: | [bold red]Error:[/bold red] {message}")


def print_success(message: str = "Success!"):
    print(f":tada: | [green]{message}[/green]")


def print_warning(message: str = "Warning!"):
    print(f":construction: | [yellow]{message}[/yellow]")
