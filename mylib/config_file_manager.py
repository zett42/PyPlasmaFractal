import os
import json
import logging
from appdirs import user_data_dir, site_data_dir

class ConfigFileManager:
    """
    Manages the storage and retrieval of configuration objects in a serialized format using JSON.
    
    This class allows storing configurations in either user-specific or site-specific directories
    determined by application details. It supports both default and custom serialization functions.

    Attributes:
        app_name (str): The name of the application.
        app_author (str): The author of the application.
        default_filename (str): The default filename for storing the configuration file.
    """

    def __init__(self, 
                 filename='config.json',
                 directory=None, sub_dir=None,
                 app_name=None, app_author=None, use_user_dir=True, 
                 save_function=None, load_function=None):
        """
        Initialize the ConfigFileManager object.

        Args:
            filename (str, optional): The name of the configuration file. Defaults to 'config.json'.
            directory (str, optional): The full directory path where the configuration file will be stored. 
                If not provided, it defaults to the user data directory or site data directory based on the value of `use_user_dir`.
            sub_dir (str, optional): The subdirectory within the directory where the configuration file will be stored.
            app_name (str, optional): The name of the application. Used to determine the default directory path.
            app_author (str, optional): The author of the application. Used to determine the default directory path.
            use_user_dir (bool, optional): If True, the user data directory will be used for the default directory path.
                If False, the site data directory will be used. Defaults to True.
            save_function (function, optional): A custom save function to be used instead of the default save function.
            load_function (function, optional): A custom load function to be used instead of the default load function.
        """
        self.app_name = app_name
        self.app_author = app_author
        self.default_filename = filename

        if directory:
            self.directory = directory
        else:
            self.directory = user_data_dir(app_name, app_author) if use_user_dir else site_data_dir(app_name, app_author)
        
        if sub_dir:
            self.directory = os.path.join(self.directory, sub_dir)
        
        self.save_function = save_function or self._default_save
        self.load_function = load_function or self._default_load


    @staticmethod
    def _default_save(obj):
        """ Default JSON save function. """
        return json.dumps(obj, indent=4)


    @staticmethod
    def _default_load(json_str):
        """ Default JSON load function. """
        return json.loads(json_str)


    def save_config(self, config_object, filename=None):
        """
        Saves the configuration object to a file within the specified directory.

        Parameters:
            config_object (object): The configuration object to save.
            filename (str, optional): The filename to use for saving the object. Uses default_filename if None.

        Raises:
            OSError: If the directory creation fails.
        """
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

        file_path = os.path.join(self.directory, filename or self.default_filename)
        logging.debug(f"Saving configuration to: {file_path}")

        serialized_data = self.save_function(config_object)
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(serialized_data)


    def load_config(self, filename=None, must_exist=False):
        """
        Loads a configuration object from a file in the specified directory.

        Parameters:
            filename (str, optional): The filename from which to load the configuration. Uses default_filename if None.
            must_exist (bool, optional): If True, raises FileNotFoundError if the file does not exist. Returns None if False.

        Returns:
            object: The loaded configuration object, or None if the file does not exist and must_exist is False.

        Raises:
            FileNotFoundError: If the file does not exist and must_exist is True.
        """
        file_path = os.path.join(self.directory, filename or self.default_filename)
        logging.debug(f"Loading configuration from: {file_path}")

        if not os.path.exists(file_path):
            if must_exist:
                raise FileNotFoundError(f"Configuration file '{file_path}' not found.")
            return None
        
        with open(file_path, 'r', encoding='utf-8') as file:
            serialized_data = file.read().strip()

        return self.load_function(serialized_data) if serialized_data else None
