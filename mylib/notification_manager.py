
class NotificationManager:
    """
    A class that manages notifications.

    Attributes:
        notifications (dict): A dictionary to store the notifications and their status.
    """

    def __init__(self):

        self.notifications = {}

    def push_notification(self, notification):
        """Mark a notification as active."""
        
        self.notifications[notification] = True

    def pull_notification(self, notification):
        """Check the status of a notification and clear it.

        Args:
            notification (str): The notification to check.

        Returns:
            bool: The status of the notification. True if active, False otherwise.
        """
        return self.notifications.pop(notification, False)
