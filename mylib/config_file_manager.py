import os
import json
import logging
from typing import Any

class ConfigFileManager:
    """
    Manages the storage and retrieval of configuration data, facilitating operations such as saving and loading from a specified directory.

    The class is designed to be flexible, accommodating different serialization formats beyond the default JSON. Users can provide custom 
    functions for serialization and deserialization, allowing for handling of any data format that can be converted to and from a string.
    This flexibility makes it suitable for a wide range of configuration management needs.

    Attributes:
        directory (str): The directory path where the configuration files are stored.
        default_filename (str): The default filename used for storing and retrieving the configuration file.
        save_function (callable): Function for serializing objects into strings. Defaults to a JSON serialization with indentation.
        load_function (callable): Function for deserializing strings into objects. Defaults to standard JSON deserialization.

    Methods:
        save_config(config_object, filename=None): Saves the configuration object to a file using the specified or default filename.
        load_config(filename=None, must_exist=False): Loads a configuration object from a file. Raises FileNotFoundError if
                                                      the file does not exist and 'must_exist' is set to True.
    """

    def __init__(self, directory: str, filename='config.json', save_function=None, load_function=None):
        """
        Initializes the ConfigFileManager with the necessary details for configuration file management.

        This constructor sets up the manager to handle configuration files stored in the specified directory
        and allows for using custom serialization functions. While the default serialization functions operate
        on JSON, the class is designed to support any format that can be represented as a string, making it
        versatile for various data handling needs.

        Args:
            directory (str): The full directory path where the configuration files will be managed. This path
                            should be provided by the user or determined by an external path management system.
            filename (str, optional): The name of the configuration file. Defaults to 'config.json', which will be used
                                    for saving and loading the configuration unless another filename is specified at the
                                    time of calling save_config or load_config.
            save_function (callable, optional): A function that takes a Python object and returns a string.
                                                If not specified, a default function that formats JSON will be used.
            load_function (callable, optional): A function that takes a string and returns a Python object.
                                                If not specified, the standard JSON parsing method is used.
        """
        self.directory = directory
        self.default_filename = filename
        
        self.save_function = save_function or self._default_save
        self.load_function = load_function or self._default_load


    @staticmethod
    def _default_save(obj: Any):
        """ Default JSON save function. """
        return json.dumps(obj, indent=4)


    @staticmethod
    def _default_load(json_str: str):
        """ Default JSON load function. """
        return json.loads(json_str)


    def save_config(self, config_object: Any, filename:str=None):
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


    def load_config(self, filename:str=None, must_exist:bool=False):
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
