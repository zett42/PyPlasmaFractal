import os
import pickle
from appdirs import user_data_dir
import logging
 
class ConfigFileManager:
    """
    A class for managing configuration files.

    Args:
        app_name (str): The name of the application.
        app_author (str): The author of the application.

    Attributes:
        app_name (str): The name of the application.
        app_author (str): The author of the application.
        directory (str): The directory where the configuration files are stored.

    Methods:
        save_config: Save a configuration object to a file.
        load_config: Load a configuration object from a file.
    """

    def __init__(self, app_name, app_author):
        self.app_name = app_name
        self.app_author = app_author
        self.directory = user_data_dir(app_name, app_author)
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

    def save_config(self, config_object, filename):
        """
        Save a configuration object to a file.

        Args:
            config_object: The configuration object to be saved.
            filename (str): The name of the file to save the configuration to.
        """
        filepath = os.path.join(self.directory, filename)
        with open(filepath, 'wb') as file:
            pickle.dump(config_object, file)
        logging.debug(f"Configuration saved to: {filepath}")

    def load_config(self, filename):
        """
        Load a configuration object from a file.

        Args:
            filename (str): The name of the file to load the configuration from.

        Returns:
            The loaded configuration object or None if an error occurs during unpickling.
        """
        filepath = os.path.join(self.directory, filename)
        with open(filepath, 'rb') as file:
            try:
                result = pickle.load(file)
            except pickle.UnpicklingError as e:
                logging.error(f"Could not load configuration from {filename}: {str(e)}")
                return None

            logging.debug(f"Configuration loaded from: {filepath}")
            return result
