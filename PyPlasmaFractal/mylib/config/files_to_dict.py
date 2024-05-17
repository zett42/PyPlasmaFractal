from pathlib import Path

def read_directory_files_to_dict(directory_path: str, recursive: bool = False) -> dict[str, str]:
    """
    Reads text files in a directory and returns a dictionary where the keys are the relative paths of the files
    and the values are the contents of the files.

    Args:
        directory_path (str): The path to the directory.
        recursive (bool, optional): Whether to recursively process subdirectories. Defaults to False.

    Returns:
        dict[str, str]: A dictionary where the keys are the relative paths of the files (with Unix-style path separators)
        and the values are the contents of the files.

    Raises:
        FileNotFoundError: If the specified directory does not exist.
        Exception: If there is an error reading a file.

    """
    base_path = Path(directory_path)
    if not base_path.exists():
        raise FileNotFoundError(f"The directory {directory_path} does not exist.")
    
    files_dict = {}

    def process_directory(path: Path, base_path: Path):
        for entry in path.iterdir():
            if entry.is_file():
                # Normalize path separators to forward slashes
                relative_path = entry.relative_to(base_path).as_posix()
                try:
                    with entry.open('r', encoding='utf-8') as file:
                        files_dict[str(relative_path)] = file.read()
                except Exception as e:
                    raise Exception(f"Error reading file {relative_path}: {str(e)}")
            elif entry.is_dir() and recursive:
                process_directory(entry, base_path)

    process_directory(base_path, base_path)

    return files_dict
