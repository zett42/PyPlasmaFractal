import os
from appdirs import user_data_dir, site_data_dir
import logging

class ConfigFileManager:
    """
    Manages the storage and retrieval of configuration objects in a serialized format.
    Configurations are stored in a directory determined by the application name and author, with options for user-specific
    or site-specific data directories.
    """

    def __init__(self, app_name, app_author, 
                 sub_dir=None,
                 filename='config.json', 
                 use_user_dir=True, 
                 custom_user_dir=None, custom_site_dir=None,
                 model_class=None,
                 save_function=None, load_function=None):
        """
        Initialize the ConfigFileManager object.

        Args:
            app_name (str): The name of the application.
            app_author (str): The author of the application.
            sub_dir (str, optional): A subdirectory within the user or site directory to store the configuration file.
            filename (str, optional): The name of the config file. Defaults to 'config.json'.
            use_user_dir (bool, optional): Whether to use the user directory for loading and saving the config file. 
                                           Defaults to True.
            custom_user_dir (str, optional): A custom path for the user directory. If provided, overrides the default 
                                             user directory. Defaults to None.
            custom_site_dir (str, optional): A custom path for the site directory. Used only when use_user_dir is False. 
                                             Defaults to None.
            model_class (type, optional): The class to use for loading from and saving to the config file. If provided, 
                                          defaults for loading and saving functions are set to use model_class.from_json() 
                                          and .to_json(), respectively. Defaults to None.
            save_function (callable, optional): A custom function to serialize the configuration data. If not provided 
                                                and model_class is not set, the default is to call .to_json() on the object 
                                                being saved. Defaults to None.
            load_function (callable, optional): A custom function to deserialize the configuration data. If not provided 
                                                and model_class is set, the default is to use model_class.from_json(). 
                                                Defaults to None.
        Raises:
            ValueError: If neither load_function nor model_class with a from_json method is provided.
        """
        self.app_name = app_name
        self.app_author = app_author
        self.default_filename = filename

        # Determine the save directory (always user directory)
        self.save_directory = custom_user_dir or user_data_dir(app_name, app_author)

        # Determine the load directory based on user or site preference
        if use_user_dir:
            self.load_directory = custom_user_dir or user_data_dir(app_name, app_author)
        else:
            self.load_directory = custom_site_dir or site_data_dir(app_name, app_author)

        # Add a subdirectory if provided
        self.save_directory = os.path.join(self.save_directory, sub_dir) if sub_dir else self.save_directory
        self.load_directory = os.path.join(self.load_directory, sub_dir) if sub_dir else self.load_directory

        # Default serialization methods, using class-specific methods if available and no custom function is provided
        self.save_function = save_function if save_function else lambda obj: obj.to_json()
        if load_function:
            self.load_function = load_function
        elif model_class:
            self.load_function = lambda data: model_class.from_json(data)
        else:
            raise ValueError("A load function or a class with a from_json method must be provided")

        self.model_class = model_class


    def save_config(self, config_object, filename=None):
        """
        Save the configuration object to a file.
        Args:
            config_object: The configuration object to be saved.
            filename (str, optional): The name of the file to save the configuration to. If not provided,
                                      the default filename will be used.
        Returns:
            None
        """

        # Ensure the save directory exists
        if not os.path.exists(self.save_directory):
            os.makedirs(self.save_directory)

        file_path = os.path.join(self.save_directory, filename or self.default_filename)
        logging.debug(f"Saving configuration to: {file_path}")

        # Serialize the object to a string and write it to the file
        serialized_data = self.save_function(config_object)

        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(serialized_data)


    def load_config(self, filename=None, must_exist=True):
        """
        Load a configuration file.
        Args:
            filename (str, optional): The name of the configuration file to load. If not provided,
                                      the default filename will be used.
            must_exist (bool, optional): Whether the file must exist. If False and file does not exist, returns None.
        Returns:
            object: The loaded configuration object or None if the file does not exist and must_exist is False.
        Raises:
            FileNotFoundError: If the file does not exist and must_exist is True.
        """
        file_path = os.path.join(self.load_directory, filename or self.default_filename)
        logging.debug(f"Loading configuration from: {file_path}")
        
        if not os.path.exists(file_path):
            if must_exist:
                raise FileNotFoundError(f"Configuration file '{file_path}' not found.")
            else:
                return None
        
        with open(file_path, 'r', encoding='utf-8') as file:
            serialized_data = file.read().strip()

        # Deserialize the content if it is not empty; otherwise return None
        return self.load_function(serialized_data) if serialized_data else None


    def load_config_or_default(self, filename=None):
        """
        Load the configuration or return a default instance if the file does not exist or content is empty.
        
        Args:
            filename (str, optional): The name of the configuration file to load. If not provided, the default
                                      filename will be used.
        
        Returns:
            object: The loaded configuration object, or a default instance of model_class if not found.
        """
        config = self.load_config(filename, must_exist=False)

        if config is None and self.model_class:
            return self.model_class()

        return config
