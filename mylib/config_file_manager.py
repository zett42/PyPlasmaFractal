import os
import pickle
from appdirs import user_data_dir, site_data_dir
import logging


class ConfigFileManager:
    """
    Manages the storage and retrieval of configuration objects in a serialized format using pickle.
    Configurations are stored in a directory determined by the application name and author, with options for user-specific
    or site-specific data directories.

    Attributes:
        app_name (str): The name of the application.
        app_author (str): The author of the application.
        default_filename (str): Default filename for saving the configuration file.
        load_directory (str): The directory path used for loading the configuration files.

    Args:
        app_name (str): The name of the application.
        app_author (str): The author of the application.
        filename (str, optional): The default filename for the configuration file. Defaults to 'config.pkl'.
        use_user_dir (bool, optional): Whether to use the user directory by default for loading configs. Defaults to True.
        custom_user_dir (str, optional): Custom path for the user directory. Defaults to None.
        custom_site_dir (str, optional): Custom path for the site directory. Defaults to None.
    """

    def __init__(self, app_name, app_author, filename='config.pkl', use_user_dir=True, custom_user_dir=None, custom_site_dir=None):
        """
        Initializes a new instance of the ConfigFileManager, creating the necessary directory for storing configuration files.

        Args:
            app_name (str): The name of the application.
            app_author (str): The author of the application.
            filename (str, optional): The default filename for the configuration file. Defaults to 'config.pkl'.
            use_user_dir (bool, optional): Whether to use the user directory by default for loading configs. Defaults to True.
            custom_user_dir (str, optional): Custom path for the user directory. Defaults to None.
            custom_site_dir (str, optional): Custom path for the site directory. Defaults to None.
        """
        self.app_name = app_name
        self.app_author = app_author
        self.default_filename = filename
        
        # The save directory is always the user directory, because the site directory typically is read-only 
        self.save_directory = custom_user_dir if custom_user_dir else user_data_dir(app_name, app_author)

        # The load directory can be either the user directory or the site directory
        if use_user_dir:
            self.load_directory = custom_user_dir or user_data_dir(app_name, app_author)
        else:
            self.load_directory = custom_site_dir or site_data_dir(app_name, app_author)
        
        # Ensure the save directory is created
        if not os.path.exists(self.save_directory):
            os.makedirs(self.save_directory)


    def save_config(self, config_object, filename=None):
        """
        Saves a configuration object to a file in the user directory using pickle serialization.

        Args:
            config_object: The configuration object to be saved. This should be pickle-serializable.
            filename (str, optional): The filename to use for saving the file. If None, the default_filename is used.

        Raises:
            OSError: If there is an issue writing to the file.
        """
        file_path = os.path.join(self.save_directory, filename or self.default_filename)

        with open(file_path, 'wb') as file:
            pickle.dump(config_object, file)
        
        logging.debug(f"Configuration saved to: {file_path}")


    def load_config(self, filename=None):
        """
        Loads a configuration object from a file using pickle deserialization, based on the default directory setup.
        If a filename is provided, updates the default filename used for future operations.

        Args:
            filename (str, optional): The filename from which to load the configuration. If None, the default_filename is used.

        Returns:
            The loaded configuration object, or None if an error occurs during unpickling.

        Raises:
            FileNotFoundError: If the specified file does not exist.
            pickle.UnpicklingError: If the file cannot be unpickled.
        """
        if filename:
            self.default_filename = filename

        filepath = os.path.join(self.load_directory, filename or self.default_filename)

        if not os.path.exists(filepath):
            raise FileNotFoundError(f"No such file: {filepath}")

        with open(filepath, 'rb') as file:
            result = pickle.load(file)

            logging.debug(f"Configuration loaded from: {filepath}")

            return result