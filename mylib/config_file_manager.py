import os
import pickle
from appdirs import user_data_dir
import logging

class ConfigFileManager:
    """
    Manages the storage and retrieval of configuration objects in a serialized format using pickle.
    Configurations are stored in a user-specific data directory determined by the application name and author.

    Attributes:
        app_name (str): The name of the application.
        app_author (str): The author of the application.
        directory (str): The directory path where the configuration files are stored.
        default_filename (str): Default filename for saving the configuration file.

    Args:
        app_name (str): The name of the application.
        app_author (str): The author of the application.
        filename (str, optional): The default filename for the configuration file. Defaults to 'config.pkl'.
    """

    def __init__(self, app_name, app_author, filename='config.pkl'):
        """
        Initializes a new instance of the ConfigFileManager, creating the necessary directory for storing configuration files.

        Args:
            app_name (str): The name of the application.
            app_author (str): The author of the application.
            filename (str, optional): The default filename for the configuration file. Defaults to 'config.pkl'.
        """
        self.app_name = app_name
        self.app_author = app_author
        self.default_filename = filename
        self.directory = user_data_dir(app_name, app_author)
        
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

    def save_config(self, config_object, filename=None):
        """
        Saves a configuration object to a file in the specified directory using pickle serialization.

        Args:
            config_object: The configuration object to be saved. This should be pickle-serializable.
            filename (str, optional): The filename to use for saving the file. If None, the default_filename is used.

        Raises:
            OSError: If there is an issue writing to the file.
        """
        file_path = os.path.join(self.directory, filename or self.default_filename)
        with open(file_path, 'wb') as file:
            pickle.dump(config_object, file)
        
        logging.debug(f"Configuration saved to: {file_path}")

    def load_config(self, filename=None):
        """
        Loads a configuration object from a file in the specified directory using pickle deserialization.

        Args:
            filename (str, optional): The filename from which to load the configuration. If None, the default_filename is used.

        Returns:
            The loaded configuration object, or None if an error occurs during unpickling.

        Raises:
            FileNotFoundError: If the specified file does not exist.
            pickle.UnpicklingError: If the file cannot be unpickled.
        """
        filepath = os.path.join(self.directory, filename or self.default_filename)
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"No such file: {filepath}")

        with open(filepath, 'rb') as file:
            try:
                result = pickle.load(file)
            except pickle.UnpicklingError as e:
                logging.error(f"Could not load configuration from {filepath}: {str(e)}")
                return None

            logging.debug(f"Configuration loaded from: {filepath}")
            return result
