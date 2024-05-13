from enum import Enum
import json
from pathlib import Path
from mylib.config.storage import *


class EnumJSONEncoder(json.JSONEncoder):
    """ Custom JSON encoder for Enum objects (which are not serializable by default)."""
    
    def default(self, obj):
        if isinstance(obj, Enum):
            return obj.name
        return json.JSONEncoder.default(self, obj)


class JsonFileStorage(Storage):
    """
    A class that provides storage operations for JSON files.
    """

    def __init__(self, base_dir: str) -> None:
        """
        Initialize a JsonFileStorage object from a directory path.

        Args:
            base_dir (str): The base directory where the JSON files will be stored.

        Raises:
            StorageCreateDirectoryError: If the directory cannot be created.

        """
        self.base_dir = Path(base_dir)
        try:
            self.base_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise StorageCreateDirectoryError(str(self.base_dir), "Could not create directory") from e


    def load(self, filename: str) -> Dict[str, Any]:
        """
        Load a JSON file from the storage directory.

        Args:
            filename (str): The name of the JSON file to load.

        Returns:
            Dict[str, Any]: The loaded JSON data.

        Raises:
            StorageItemNotFoundError: If the specified file is not found.
            StorageItemLoadError: If the JSON file cannot be loaded.
        """
        # Add the .json extension to the filename, if missing
        filename = filename if filename.lower().endswith('.json') else filename + '.json'
        path = self.base_dir / filename
        try:
            with path.open('r') as file:
                return json.load(file)
        except FileNotFoundError as e:
            raise StorageItemNotFoundError(filename, "File not found") from e
        except Exception as e:
            raise StorageItemLoadError(filename, "Could not load JSON file") from e


    def save(self, data: Dict[str, Any], filename: str) -> None:
        """
        Save JSON data to a file in the storage directory.

        Args:
            data (Dict[str, Any]): The JSON data to save.
            filename (str): The name of the JSON file to save.

        Raises:
            StorageItemSaveError: If the JSON file cannot be saved.
        """
        # Add the .json extension to the filename, if missing
        filename = filename if filename.lower().endswith('.json') else filename + '.json'        
        path = self.base_dir / filename
        try:
            with path.open('w') as file:
                json.dump(data, file, indent=4, cls=EnumJSONEncoder)
        except Exception as e:
            raise StorageItemSaveError(filename, "Could not save JSON file") from e


    def delete(self, filename: str) -> None:
        """
        Delete a JSON file from the storage directory.

        Args:
            filename (str): The name of the JSON file to delete.

        Raises:
            StorageItemNotFoundError: If the specified file is not found.
            StorageItemDeletionError: If the file cannot be deleted.
        """
        path = self.base_dir / filename
        try:
            path.unlink()
        except FileNotFoundError as e:
            raise StorageItemNotFoundError(filename, "File not found") from e
        except Exception as e:
            raise StorageItemDeletionError(filename, "Could not delete file") from e


    def list(self) -> List[str]:
        """
        List all JSON files in the storage directory.

        Returns:
            List[str]: A list of filenames of all JSON files.

        Raises:
            StorageItemListingError: If the files in the directory cannot be listed.
        """
        try:
            return [file.name for file in self.base_dir.glob('*.json')]
        except Exception as e:
            raise StorageItemListingError(str(self.base_dir), "Could not list files from directory") from e
