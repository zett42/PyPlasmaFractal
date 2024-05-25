from typing import List
from pathlib import Path
from PyPlasmaFractal.mylib.config.storage import *

class DictTextFileStorage(Storage[str]):
    """
    A storage class that stores text file contents in a dictionary.
    The filenames are the keys and their content is the value.
    """

    def __init__(self, base_directory: str = None, pattern: str = '*.txt', recurse: bool = True) -> None:
        """
        Initialize a DictFileStorage object with an optional base directory.

        Args:
            base_directory (str, optional): The directory where the text files are stored.
            pattern (str, optional): The wildcard pattern to filter files. Defaults to '*.txt'.
        """
        self.storage_dict = {}
        if base_directory:
            self.load_from_directory(base_directory, pattern, recurse)

    def save(self, data: str, filename: str) -> None:
        """
        Save the content of a text file to the storage dictionary.

        Args:
            data (str): The content to save.
            filename (str): The name of the text file to save.
        """
        self.storage_dict[filename] = data

    def load(self, filename: str) -> str:
        """
        Load the content of a text file from the storage dictionary.

        Args:
            filename (str): The name of the text file to load.

        Returns:
            str: The content of the text file.

        Raises:
            StorageItemNotFoundError: If the specified file is not found.
        """
        if filename in self.storage_dict:
            return self.storage_dict[filename]
        else:
            raise StorageItemNotFoundError(filename, "File not found")

    def delete(self, filename: str) -> None:
        """
        Delete the content of a text file from the storage dictionary.

        Args:
            filename (str): The name of the text file to delete.

        Raises:
            StorageItemNotFoundError: If the specified file is not found.
            StorageItemDeletionError: If the file cannot be deleted.
        """
        if filename in self.storage_dict:
            del self.storage_dict[filename]
        else:
            raise StorageItemNotFoundError(filename, "File not found")

    def list(self) -> List[str]:
        """
        List all text files in the storage dictionary.

        Returns:
            List[str]: A list of filenames of all text files.
        
        Raises:
            StorageItemListingError: If the files in the directory cannot be listed.
        """
        try:
            return list(self.storage_dict.keys())
        except Exception as e:
            raise StorageItemListingError("Could not list files from dictionary") from e

    def exists(self, filename: str) -> bool:
        """
        Check if a text file exists in the storage dictionary.

        Args:
            filename (str): The name of the text file to check.

        Returns:
            bool: True if the file exists, False otherwise.
        """
        return filename in self.storage_dict
    
    def get_full_path(self, filename: str) -> str:
        """
        Get the full path of a text file in the storage dictionary.

        Args:
            filename (str): The name of the text file.

        Returns:
            str: The full path of the text file.
        """
        return filename

    def load_from_directory(self, base_directory: str, pattern: str, recurse: bool = True) -> None:
        """
        Load all text files matching the pattern from the base directory into the storage dictionary.

        Args:
            base_directory (str): The base directory where the text files are stored.
            pattern (str): The wildcard pattern to filter files.
            recurse (bool, optional): Whether to load files recursively. Defaults to True.
        """
        base_path = Path(base_directory)
        glob_method = base_path.rglob if recurse else base_path.glob
        
        for file_path in glob_method(pattern):
            
            relative_path = file_path.relative_to(base_path).as_posix()
            
            with file_path.open('r') as file:
                self.storage_dict[relative_path] = file.read()