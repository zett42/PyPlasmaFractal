from enum import Enum, auto
from dataclasses import dataclass
from typing import List

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

    def list_items(self) -> List['StorageSourceManager.Item']:
        """
        Lists all the items from both app and user storage.

        Returns:
            List[StorageSourceManager.Item]: A list of items from both app and user storage.
        """
        app_items  = [self.Item(name=name, source=self.Source.APP)  for name in self.app_storage.list()]
        user_items = [self.Item(name=name, source=self.Source.USER) for name in self.user_storage.list()]
        return app_items + user_items
