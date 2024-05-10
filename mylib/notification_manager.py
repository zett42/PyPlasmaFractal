class NotificationManager:
    """
    A class that manages notifications, storing arbitrary data for each notification.
    
    Attributes:
        notifications (dict): A dictionary to store arbitrary data associated with notifications.
    """

    def __init__(self):
        # Initialize the dictionary to store notification data
        self.notifications = {}


    def push_notification(self, notification, data = None):
        """
        Add or update a notification with associated data.
        
        Args:
            notification (str): The identifier for the notification.
            data (any): Arbitrary data to associate with the notification.
        """
        self.notifications[notification] = data


    def pull_notification(self, notification):
        """
        Retrieve the data for a notification and remove it from active notifications.
        
        Args:
            notification (str): The notification to retrieve data for.

        Returns:
            any: The data associated with the notification, or None if the notification does not exist.
        """
        return self.notifications.pop(notification, None)


    def peek_notification(self, notification):
        """
        Retrieve the data for a notification without removing it from active notifications.
        It can also be used to check if a notification exists, by checking for None return value.
        
        Args:
            notification (str): The notification to retrieve data for.

        Returns:
            any: The data associated with the notification, or None if the notification does not exist.
        """
        return self.notifications.get(notification, None)