import os
import tempfile
import subprocess


def edit_text(initial_text: str = "") -> str:
    # Create a temporary file
    with tempfile.NamedTemporaryFile(suffix=".tmp", delete=False) as temp_file:
        temp_file_name = temp_file.name
        temp_file.write(initial_text.encode())
        temp_file.flush()

    # Open the temporary file in the user's default text editor
    editor = os.getenv("EDITOR", "nano")  # Default to nano if $EDITOR is not set
    subprocess.call([editor, temp_file_name])

    # Read the edited content
    with open(temp_file_name, "r") as temp_file:
        edited_text = temp_file.read()

    # Clean up
    os.remove(temp_file_name)

    return edited_text.strip()
