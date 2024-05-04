import logging
import os

class Preset:
    """
    Represents a preset with its full directory path and relative file path.
    
    Attributes:
        directory (str): The full directory path where the preset file is located.
        relative_file_path (str): The relative path to the preset file.
        is_predefined (bool): True if this is a built-in application preset, False otherwise.
    """
    def __init__(self, directory: str, relative_file_path: str, is_predefined: bool):
        self.directory = directory
        self.relative_file_path = relative_file_path
        self.is_predefined = is_predefined

    def __repr__(self):
        return f"Preset(directory='{self.directory}', relative_file_path='{self.relative_file_path}', is_predefined={self.is_predefined})"


def list_presets(app_dir: str, user_dir: str):
    """
    List all preset files from the application's built-in directory and the user's directory,
    marking them as predefined or user-defined and including their full paths.
    
    Args:
    app_dir (str): Path to the application's built-in presets directory.
    user_dir (str): Path to the user's presets directory.
    
    Returns:
    list: A list of Preset objects representing all preset files found in both directories.
    """
    def create_presets_list(directory: str, is_predefined: bool):
        presets = []
        try:
            for f in os.listdir(directory):
                if f.endswith('.json'):
                    presets.append(Preset(directory, f, is_predefined))
        except FileNotFoundError:
            # If the directory does not exist, return an empty list
            pass
        return presets

    # Create lists of presets from both directories
    app_presets = create_presets_list(app_dir, True)
    user_presets = create_presets_list(user_dir, False)
    
    # Combine results
    all_presets = app_presets + user_presets

    return all_presets


def load_preset(preset: Preset) -> str:
    """
    Load the configuration from a preset file based on the provided Preset object.
    
    Args:
    preset (Preset): The preset object containing the directory, relative file path, and predefined status.

    Returns:
    Raw string data from the preset file.
    """
    full_path = os.path.join(preset.directory, preset.relative_file_path)
    
    with open(full_path, 'r') as file:
        preset_data = file.read()
    
    logging.info(f"Preset loaded successfully from {full_path}")

    return preset_data


def save_preset(file_path: str, data: str):
    """
    Save the configuration data to a preset file based on the provided Preset object.
    
    Args:
    file_path (str): The full path to the preset file.
    data (str): The configuration data to be saved to the preset file.
    """

    # Create the directory if it does not exist
    directory = os.path.dirname(file_path)
    os.makedirs(directory, exist_ok=True)

    with open(file_path, 'w') as file:
        file.write(data)
    
    logging.info(f"Preset saved successfully to {file_path}")


def delete_preset(file_path: str):
    """
    Delete a preset file based on the provided file path.
    
    Args:
    file_path (str): The full path to the preset file to be deleted.
    """
    
    os.remove(file_path)

    logging.info(f"Preset deleted successfully from {file_path}")
    