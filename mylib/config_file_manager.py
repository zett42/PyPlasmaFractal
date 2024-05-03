import os
from appdirs import user_data_dir, site_data_dir
import logging

class ConfigFileManager:
    """
    Manages the storage and retrieval of configuration objects in a serialized format.
    Configurations are stored in a directory determined by the application name and author, with options for user-specific
    or site-specific data directories.
    """

    def __init__(self, app_name, app_author, filename='config.pkl', use_user_dir=True, custom_user_dir=None, custom_site_dir=None, save_function=None, load_function=None):

        self.app_name = app_name
        self.app_author = app_author
        self.default_filename = filename
        self.save_function = save_function
        self.load_function = load_function

        # Determine the save directory (always user directory)
        self.save_directory = custom_user_dir or user_data_dir(app_name, app_author)

        # Determine the load directory based on user or site preference
        if use_user_dir:
            self.load_directory = custom_user_dir or user_data_dir(app_name, app_author)
        else:
            self.load_directory = custom_site_dir or site_data_dir(app_name, app_author)

        # Ensure the save directory exists
        if not os.path.exists(self.save_directory):
            os.makedirs(self.save_directory)


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

        file_path = os.path.join(self.save_directory, filename or self.default_filename)
        logging.debug(f"Saving configuration to: {file_path}")

        # Serialize the object to a string and write it to the file
        config_data = self.save_function(config_object)
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(config_data)

        logging.debug(f"Configuration saved to: {file_path}")


    def load_config(self, filename=None):

        if filename:
            self.default_filename = filename

        file_path = os.path.join(self.load_directory, filename or self.default_filename)
        logging.debug(f"Loading configuration from: {file_path}")

        if not os.path.exists(file_path):
            return None

        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            # Return None if the content is empty
            if not content.strip():
                return None

        return self.load_function(content)
