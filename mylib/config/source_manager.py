from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Optional

from mylib.config.storage import Storage

class StorageSourceManager:
    """
    A class that manages the sources of storage items, e. g. configuration files.

    Attributes:
        app_storage (Storage): The storage for app-specific items.
        user_storage (Storage): The storage for user-specific items.
    """

    class Source(Enum):
        APP = auto()
        USER = auto()


    @dataclass(frozen=True)
    class Item:
        """
        Represents an item in the storage.

        Attributes:
            name (str): The name of the item.
            source (StorageSourceManager.Source): The source of the item.
        """
        name: str
        source: 'StorageSourceManager.Source'


    def __init__(self, app_storage: Storage, user_storage: Storage) -> None:
        """
        Initializes a new instance of the StorageSourceManager class.

        Args:
            app_storage (Storage): The storage for app-specific items.
            user_storage (Storage): The storage for user-specific items.
        """
        self.app_storage = app_storage
        self.user_storage = user_storage


    def get_storage(self, source: 'StorageSourceManager.Source') -> Storage:
        """
        Returns the storage for the specified source.

        Args:
            source (StorageSourceManager.Source): The source of the storage.

        Returns:
            Storage: The storage for the specified source.
        """
        return self.app_storage if source == self.Source.APP else self.user_storage
    

    def list_items(self, sources: Optional[List['StorageSourceManager.Source']] = None) -> List['StorageSourceManager.Item']:
        """
        Lists items from specified storage sources.

        Args:
            sources (Optional[List[StorageSourceManager.Source]]): The list of sources to include. 
                If None, includes all sources.

        Returns:
            List[StorageSourceManager.Item]: A list of items from the specified storage sources.
        """
        sources = sources or [self.Source.APP, self.Source.USER]

        items = []
        if self.Source.APP in sources:
            items.extend(self.Item(name=name, source=self.Source.APP) for name in self.app_storage.list())
        if self.Source.USER in sources:
            items.extend(self.Item(name=name, source=self.Source.USER) for name in self.user_storage.list())
        
        return items
