import os

# Folder we want to scan — "." means "this current folder"
TARGET_FOLDER = r"C:\Users\Khushi\Downloads\ToDo-List-using-Flask-and-MongoDB-main\ToDo-List-using-Flask-and-MongoDB-main"

# File types we care about (skip images, binaries, etc.)
VALID_EXTENSIONS = {".py", ".md", ".txt", ".json",".html"}
# Folders to completely ignore
IGNORE_FOLDERS = {"venv", "__pycache__", ".git", "node_modules"}


def find_code_files(root_folder):
    """Walk through the folder and return paths of all relevant files."""
    file_paths = []
    for current_dir, dirs, files in os.walk(root_folder):
        # Skip ignored folders (modifying dirs in-place stops os.walk from entering them)
        dirs[:] = [d for d in dirs if d not in IGNORE_FOLDERS]

        for filename in files:
            if any(filename.endswith(ext) for ext in VALID_EXTENSIONS):
                full_path = os.path.join(current_dir, filename)
                file_paths.append(full_path)
    return file_paths


def chunk_text(text, chunk_size=800, overlap=100):
    """Split text into overlapping chunks so context isn't lost at chunk edges."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap  # move forward, but overlap a bit
    return chunks


def main():
    files = find_code_files(TARGET_FOLDER)
    print(f"Found {len(files)} files to process.\n")

    all_chunks = []
    for path in files:
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            print(f"Skipped {path}: {e}")
            continue

        chunks = chunk_text(content)
        for i, chunk in enumerate(chunks):
            all_chunks.append({
                "file": path,
                "chunk_index": i,
                "text": chunk
            })

    print(f"Created {len(all_chunks)} total chunks.\n")
    # Print the first chunk as a sanity check
    if all_chunks:
        print("--- Example chunk ---")
        print(f"File: {all_chunks[0]['file']}")
        print(f"Text preview: {all_chunks[0]['text'][:200]}...")

    return all_chunks


if __name__ == "__main__":
    main()