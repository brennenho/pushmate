def parse_pr(text):
    first_newline_index = text.find("\n")

    # Extract the title and remove leading "Title: " and trailing spaces
    title = text[0:first_newline_index].replace("Title: ", "").strip()

    # Extract the body by removing the title line and leading/trailing whitespaces
    body = text[first_newline_index:].strip()

    return title, body
