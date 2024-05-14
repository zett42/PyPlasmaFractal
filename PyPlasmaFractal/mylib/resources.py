import os
import sys

def resource_path(relative_path: str) -> str:
    """ Get absolute path to resource, works for dev and for PyInstaller. 
    Assumes that this script is located within a sub directory relative to the main script. """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = os.path.join(sys._MEIPASS, 'PyPlasmaFractal')
    except AttributeError:
        # In development, the base path should be two directories up
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)
