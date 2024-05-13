import os

def read_directory_files_to_dict(directory_path: str, recursive: bool = False) -> dict[str, str]:
    """
    Reads text files in a directory and returns a dictionary where the keys are the relative paths of the files
    and the values are the contents of the files.

    Args:
        directory_path (str): The path to the directory.
        recursive (bool, optional): Whether to recursively process subdirectories. Defaults to False.

    Returns:
        dict[str, str]: A dictionary where the keys are the relative paths of the files and the values are
        the contents of the files.

    Raises:
        FileNotFoundError: If the specified directory does not exist.
        Exception: If there is an error reading a file.

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