import os

class Preset:
    """
    Represents a preset with its file path and a flag indicating if it's a predefined application preset.
    
    Attributes:
        file_path (str): The relative path to the preset file.
        is_predefined (bool): True if this is a built-in application preset, False otherwise.
    """
    def __init__(self, file_path: str, is_predefined: bool):
        self.file_path = file_path
        self.is_predefined = is_predefined

    def __repr__(self):
        return f"Preset(file_path='{self.file_path}', is_predefined={self.is_predefined})"


def list_presets(app_dir: str, user_dir: str):
    """
    List all preset files from the application's built-in directory and the user's directory,
    marking them as predefined or user-defined.
    
    Args:
    app_dir (str): Path to the application's built-in presets directory.
    user_dir (str): Path to the user's presets directory.
    
    Returns:
    list: List of Preset instances.
    """
    # Helper function to create preset objects from directory contents
    def create_presets_list(directory: str, is_predefined: bool):
        
        presets = []
        try:
            for f in os.listdir(directory):
                if f.endswith('.json'):
                    presets.append(Preset(file_path=f, is_predefined=is_predefined))
        except FileNotFoundError:
            # If the directory does not exist, return an empty list
            pass

        return presets

    # Create lists of presets from both directories
    app_presets = create_presets_list(app_dir, True)
    user_presets = create_presets_list(user_dir, False)
    
    # Combine results
    return app_presets + user_presets
