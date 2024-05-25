from abc import ABC, abstractmethod
from typing import *

DataType = TypeVar('DataType')

class Storage(ABC, Generic[DataType]):
    """
    Abstract base class for storage.

    This class defines the interface for storing, retrieving, and managing 
    data of a generic type. Implementations of this interface can handle various 
    types of data storage, such as files, databases, or cloud storage.
    """
    @abstractmethod
    def save(self, data: DataType, name: str) -> None:
        """
        Save data with the specified name.

        Args:
            data (DataType): The data to save. The type of this data is defined by the implementation.
            name (str): The name or key under which the data will be stored.

        Raises:
            StorageItemSaveError: If there is an error saving the data.
        """
        pass

    @abstractmethod
    def load(self, name: str) -> DataType:
        """
        Load data with the specified name.

        Args:
            name (str): The name or key of the data to load.

        Returns:
            DataType: The data that was loaded. The type of this data is defined by the implementation.

        Raises:
            StorageItemNotFoundError: If the data with the specified name is not found.
            StorageItemLoadError: If there is an error loading the data.
        """
        pass
    
    @abstractmethod
    def delete(self, name: str) -> None:
        """
        Delete data with the specified name.

        Args:
            name (str): The name or key of the data to delete.

        Raises:
            StorageItemNotFoundError: If the data with the specified name is not found.
            StorageItemDeletionError: If there is an error deleting the data.
        """
        pass

    @abstractmethod
    def list(self) -> List[str]:
        """
        List all names or keys of stored data.

        Returns:
            List[str]: A list of all names or keys of the stored data.

        Raises:
            StorageItemListingError: If there is an error listing the data.
        """
        pass
    
    @abstractmethod
    def exists(self, name: str) -> bool:
        """
        Check if data with the specified name exists.

        Args:
            name (str): The name or key of the data to check.

        Returns:
            bool: True if the data exists, False otherwise.
        """
        pass
    
    @abstractmethod
    def get_full_path(self, name: str) -> str:
        """
        Get the full path of the data with the specified name.

        Args:
            name (str): The name or key of the data.

        Returns:
            str: The full path of the data.
        """
        pass
    

class StorageError(Exception):
    """Base class for all storage-related exceptions."""
    def __init__(self, name: str, message: str) -> None:
        super().__init__(f"{message}: {name}")
        self.name = name

class StorageCreateDirectoryError(StorageError):
    """Exception raised when a directory could not be created."""
    def __init__(self, directory: str, message: str) -> None:
        super().__init__(directory, message)
        
class StorageItemNotFoundError(StorageError):
    """Exception raised when an item is not found."""
    def __init__(self, name: str, message: str) -> None:
        super().__init__(name, message)

class StorageItemDeletionError(StorageError):
    """Exception raised when there is an error deleting an item."""
    def __init__(self, name: str, message: str) -> None:
        super().__init__(name, message)

class StorageItemSaveError(StorageError):
    """Exception raised when saving a file fails."""
    def __init__(self, name: str, message: str) -> None:
        super().__init__(name, message)

class StorageItemLoadError(StorageError):
    """Exception raised when there is an error loading a file."""
    def __init__(self, name: str, message: str) -> None:
        super().__init__(name, message)

class StorageItemListingError(StorageError):
    """Exception raised when listing files fails."""
    def __init__(self, directory: str, message: str) -> None:
        super().__init__(directory, message)
