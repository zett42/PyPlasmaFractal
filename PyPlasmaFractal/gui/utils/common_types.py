from enum import Enum, auto

class GuiNotification(Enum):
    """Notification types for the GUI notification manager"""
    NEW_PRESET_LOADED = auto()         # Send by the GUI when a new preset is loaded
    RECORDING_STATE_CHANGED = auto()   # Send by the GUI when the recording state changes
    RECORDING_ERROR = auto()           # Received by the GUI when an error occurs during recording
    LOAD_CONFIG_ERROR = auto()         # Received by the GUI when an error occurs while loading the configuration
