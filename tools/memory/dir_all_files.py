def list_files_single_function(path):
    """
    A single-function utility that:
      1. Takes a directory path (str) as an argument.
      2. Recursively finds all files within that directory.
      3. Skips directories named 'node_modules', '.git', and any folder containing 'venv'.
      4. Skips junk files like .DS_Store, Thumbs.db, __pycache__.
      5. Returns a list of file paths (strings), relative to 'path', 
         with all backslashes replaced by forward slashes.

    Example usage:
        collected = list_files_single_function("C:/path/to/new_project")
        print(collected)
        # Possible output:
        # ["index.html", "scripts/script.js", "styles/styles.css"]
    """
    import os

    # Directories to exclude
    exclude_dirs = ["node_modules", ".git"]
    # Common junk files
    junk_files = [".DS_Store", "Thumbs.db", "__pycache__"]

    # Normalize the input path (handles things like ~, relative paths, etc.)
    path = os.path.abspath(path)

    # We'll build a list of (string) paths
    collected_files = []

    # Walk the directory
    for root, dirs, files in os.walk(path, topdown=True):
        # Filter out unwanted directories
        dirs[:] = [
            d for d in dirs
            if d not in exclude_dirs and "venv" not in d
        ]

        for file in files:
            # Skip junk files
            if file in junk_files:
                continue

            # Skip files if their path contains "venv"
            if "venv" in root:
                continue

            # Build the absolute path to the file
            abs_filepath = os.path.join(root, file)

            # Make the path relative to the directory you provided
            rel_filepath = os.path.relpath(abs_filepath, path)

            # Replace backslashes with forward slashes to normalize
            rel_filepath = rel_filepath.replace("\\", "/")

            # Append the final, normalized relative path
            collected_files.append(rel_filepath)

    return collected_files
