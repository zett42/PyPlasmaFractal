from pathlib import Path
import appdirs
from typing import Optional

class ConfigPathManager:
    def __init__(self, app_name: str, app_author: str, app_specific_path: Optional[str] = None):
        """
        Initialize the ConfigPathManager with the application name, author, and the specific path for the application.
        
        :param app_name: Name of the application to generate user-specific paths.
        :param app_author: Name of the author of the application, used in user-specific paths.
        :param app_specific_path: Path specific to the application (typically the directory of the main script).
        """
        self._app_name = app_name
        self._app_author = app_author
        self._user_specific_path = Path(appdirs.user_data_dir(app_name, app_author))
        self._app_specific_path = Path(app_specific_path) if app_specific_path is not None else None

    @property
    def app_name(self) -> str:
        """
        Return the name of the application.
        """
        return self._app_name

    @property
    def app_author(self) -> str:
        """
        Return the author of the application.
        """
        return self._app_author

    @property
    def app_specific_path(self) -> Optional[Path]:
        """
        Return the app-specific path.
        """
        return self._app_specific_path

    @property
    def user_specific_path(self) -> Path:
        """
        Return the user-specific path as determined by appdirs.
        """
        return self._user_specific_path
