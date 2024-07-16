from rich.progress import Progress


def parse_pr(text):
    first_newline_index = text.find("\n")

    # Extract the title and remove leading "Title: " and trailing spaces
    title = text[0:first_newline_index].replace("Title: ", "").strip()

    # Extract the body by removing the title line and leading/trailing whitespaces
    body = text[first_newline_index:].strip()

    return title, body


class PauseProgress:
    def __init__(self, progress: Progress) -> None:
        self._progress = progress

    def _clear_line(self) -> None:
        UP = "\x1b[1A"
        CLEAR = "\x1b[2K"
        for _ in self._progress.tasks:
            print(UP + CLEAR + UP)

    def __enter__(self):
        self._progress.stop()
        self._clear_line()
        return self._progress

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self._progress.start()
