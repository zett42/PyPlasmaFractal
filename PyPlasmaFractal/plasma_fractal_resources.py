from pathlib import Path
import sys

def resource_path(relative_path: str) -> str:
    """ Get absolute path to resource, works for dev and for PyInstaller.
    Assumes that this script is located within a sub directory relative to the main script. """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = Path(sys._MEIPASS) / 'PyPlasmaFractal'
    except AttributeError:
        # In development, the base path is the directory of the current script
        base_path = Path(__file__).resolve().parent
    return str(base_path / relative_path)
