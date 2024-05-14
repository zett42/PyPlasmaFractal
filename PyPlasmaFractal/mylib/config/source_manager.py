from dataclasses import dataclass
from typing import List, Optional

from mylib.config.storage import Storage

class StorageSourceManager:
    """
    A class that manages the sources of storage items, e.g., configuration files.

    Attributes:
        app_storage (Storage): The storage for app-specific items.
        user_storage (Storage): The storage for user-specific items.
    """

    @dataclass(frozen=True)
    class Item:
        """
        Represents an item in the storage.

        Attributes:
            name (str): The name of the item.
            storage (Storage): The storage where the item is stored.
        """
        name: str
        storage: Storage
        

    def __init__(self, app_storage: Storage, user_storage: Storage) -> None:
        """
        Initializes a new instance of the StorageSourceManager class.

        Args:
            app_storage (Storage): The storage for app-specific items.
            user_storage (Storage): The storage for user-specific items.
        """
        self.app_storage = app_storage
        self.user_storage = user_storage
        

    def list(self, storages: Optional[List[Storage]] = None) -> List['StorageSourceManager.Item']:
        """
        Lists items from specified storage instances.

        Args:
            storages (Optional[List[Storage]]): The list of storage instances to include. 
                If None, includes all storages.

        Returns:
            List[StorageSourceManager.Item]: A list of items from the specified storages.
        """
        storages = storages or [self.app_storage, self.user_storage]

        items = []
        for storage in storages:
            items.extend(self.Item(name=name, storage=storage) for name in storage.list())
        
        return items
