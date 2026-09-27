import os

TARGET_FOLDER = r"C:\Users\Khushi\Downloads\ToDo-List-using-Flask-and-MongoDB-main\ToDo-List-using-Flask-and-MongoDB-main"


def list_files():
    """Returns a list of all code files in the target repo."""
    file_list = []
    for current_dir, dirs, files in os.walk(TARGET_FOLDER):
        dirs[:] = [d for d in dirs if d not in {"venv", "__pycache__", ".git", "node_modules"}]
        for filename in files:
            file_list.append(os.path.join(current_dir, filename))
    return file_list


def read_file(filepath):
    """Reads a file. Accepts either a full path or just a filename —
    if just a filename is given, searches the repo for a matching file."""
    # If the exact path works, use it directly
    if os.path.isfile(filepath):
        target_path = filepath
    else:
        # Otherwise, search the repo for a file with this name
        target_path = None
        search_name = os.path.basename(filepath)
        for current_dir, dirs, files in os.walk(TARGET_FOLDER):
            dirs[:] = [d for d in dirs if d not in {"venv", "__pycache__", ".git", "node_modules"}]
            if search_name in files:
                target_path = os.path.join(current_dir, search_name)
                break

    if not target_path:
        return f"Error: could not find a file named '{filepath}' in the repo."

    try:
        with open(target_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"