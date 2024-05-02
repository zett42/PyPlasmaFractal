import os

def read_directory_files_to_dict(directory_path, recursive=False):
    """
    Optimized function to read files from a directory. Optionally reads recursively from subdirectories,
    mapping paths to their content using a more efficient single loop.

    Args:
        directory_path (str): The path to the root directory from which to start reading files.
        recursive (bool): If True, reads files recursively from subdirectories. Defaults to False.

    Returns:
        dict: A dictionary where each key is a path (relative if recursive, filename only if not) to a file and
              the value is the content of that file.

    Raises:
        FileNotFoundError: If the directory does not exist or cannot be accessed.
        Exception: For other issues like reading files.
    """
    if not os.path.exists(directory_path):
        raise FileNotFoundError(f"The directory {directory_path} does not exist.")
    
    files_dict = {}
    
    def process_directory(path, base_path=directory_path):
        with os.scandir(path) as entries:
            for entry in entries:
                if entry.is_file():
                    relative_path = os.path.relpath(entry.path, base_path)
                    try:
                        with open(entry.path, 'r', encoding='utf-8') as file:
                            files_dict[relative_path] = file.read()
                    except Exception as e:
                        raise Exception(f"Error reading file {relative_path}: {str(e)}")
                elif entry.is_dir() and recursive:
                    process_directory(entry.path, base_path)

    process_directory(directory_path)

    return files_dict