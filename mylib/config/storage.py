from abc import ABC, abstractmethod
from typing import *

class Storage(ABC):
    """
    Abstract base class for storage.

    This class defines the interface for storing and retrieving structured, JSON-like data.
    """
    @abstractmethod
    def save(self, data: Dict[str, Any], name: str) -> None:
        pass

    @abstractmethod
    def load(self, name: str) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def delete(self, name: str) -> None:
        pass

    @abstractmethod
    def list(self) -> List[str]:
        pass
    
    @abstractmethod
    def exists(self, name: str) -> bool:
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
