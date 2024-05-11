import logging
from typing import TypeVar, Dict, Generic, Optional, Any

# Define a type variable for the notification key
Key = TypeVar('Key')

class NotificationManager(Generic[Key]):
    """
    A class that manages notifications, storing arbitrary data for each notification.
    Keys of the notifications are of type Key.
    
    Attributes:
        notifications (dict): A dictionary to store arbitrary data associated with notifications.
    """

    def __init__(self):
        # Initialize the dictionary to store notification data
        self.notifications: Dict[Key, Any] = {}


    def push_notification(self, notification: Key, data: Optional[Any] = None) -> None:
        """
        Add or update a notification with associated data.
        
        Args:
            notification (Key): The identifier for the notification.
            data (Any): Arbitrary data to associate with the notification.
        """
        # To ensure pull_notification returns a value, we store a boolean True if no data is provided
        self.notifications[notification] = data if data is not None else True
        

    def pull_notification(self, notification: Key) -> Optional[Any]:
        """
        Retrieve the data for a notification and remove it from active notifications.
        
        Args:
            notification (Key): The notification to retrieve data for.

        Returns:
            Optional[Any]: The data associated with the notification, or None if the notification does not exist.
        """          
        return self.notifications.pop(notification, None)


    def peek_notification(self, notification: Key) -> Optional[Any]:
        """
        Retrieve the data for a notification without removing it from active notifications.
        It can also be used to check if a notification exists, by checking for None return value.
        
        Args:
            notification (Key): The notification to retrieve data for.

        Returns:
            Optional[Any]: The data associated with the notification, or None if the notification does not exist.
        """
        return self.notifications.get(notification, None)
