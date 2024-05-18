from pathlib import PurePosixPath
from io import StringIO
from datetime import datetime
import os
import stat
from typing import Optional, Iterator, Union, Dict, Any

class DictPath(PurePosixPath):
    """
    A class to represent a path in a virtual filesystem stored as a dictionary.
    The dictionary is read-only.
    
    Attributes:
        _filesystem (dict): A dictionary representing the filesystem.
    """

    def __init__(self, *args, filesystem: Optional[Dict[str, Any]] = None):
        """
        Initialize a DictPath object.

        Args:
            args: Arguments to pass to the PurePosixPath constructor.
            filesystem (dict, optional): A read-only dictionary representing the filesystem. Default is an empty filesystem.
        """
        super().__init__(*args)
        self._filesystem = filesystem or {'/': {'type': 'directory', 'content': {}, 'metadata': self._create_metadata()}}

    def _create_metadata(self) -> Dict[str, Any]:
        """
        Create a metadata dictionary with current timestamps.

        Returns:
            Dict[str, Any]: Metadata dictionary.
        """
        now = datetime.now().timestamp()
        return {'st_ctime': now, 'st_mtime': now, 'st_atime': now}

    def _get_nested_item(self, create: bool = False) -> Dict[str, Any]:
        """
        Get the nested item in the filesystem corresponding to the current path.

        Args:
            create (bool): If True, create missing directories in the path. Default is False.

        Returns:
            Dict[str, Any]: The item in the filesystem corresponding to the current path.

        Raises:
            FileNotFoundError: If the path does not exist and create is False.
        """
        path_str = str(self)
        if path_str == '/':
            return self._filesystem['/']

        path_parts = path_str.strip('/').split('/')
        current = self._filesystem['/']

        for part in path_parts:
            if part not in current['content']:
                if create:
                    current['content'][part] = {'type': 'directory', 'content': {}, 'metadata': self._create_metadata()}
                else:
                    raise FileNotFoundError(f"No such file or directory: '{path_str}'")
            current = current['content'][part]

        return current

    def _validate_type(self, expected_type: str) -> Dict[str, Any]:
        """
        Validate the type of the item at the current path.

        Args:
            expected_type (str): The expected type of the item ('file' or 'directory').

        Returns:
            Dict[str, Any]: The item in the filesystem.

        Raises:
            FileNotFoundError: If the path does not exist.
            TypeError: If the item is not of the expected type.
        """
        item = self._get_nested_item()
        if item['type'] != expected_type:
            raise TypeError(f"'{self}' is not a {expected_type}")
        return item

    def read_text(self, encoding: Optional[str] = None, errors: Optional[str] = None) -> str:
        """
        Read the content of the file as a string.

        Args:
            encoding (str, optional): The encoding to use for decoding the file. Default is None.
            errors (str, optional): The error handling scheme to use for decoding errors. Default is None.

        Returns:
            str: The content of the file.

        Raises:
            TypeError: If the current path is not a text file.
        """
        item = self._validate_type('file')
        return item['content']

    def exists(self) -> bool:
        """
        Check if the path exists in the filesystem.

        Returns:
            bool: True if the path exists, False otherwise.
        """
        try:
            self._get_nested_item()
            return True
        except FileNotFoundError:
            return False

    def is_file(self) -> bool:
        """
        Check if the path is a file.

        Returns:
            bool: True if the path is a file, False otherwise.
        """
        try:
            self._validate_type('file')
            return True
        except (FileNotFoundError, TypeError):
            return False

    def is_dir(self) -> bool:
        """
        Check if the path is a directory.

        Returns:
            bool: True if the path is a directory, False otherwise.
        """
        try:
            self._validate_type('directory')
            return True
        except (FileNotFoundError, TypeError):
            return False

    def iterdir(self) -> Iterator['DictPath']:
        """
        Iterate over the items in the directory.

        Yields:
            DictPath: A DictPath object for each item in the directory.

        Raises:
            NotADirectoryError: If the current path is not a directory.
        """
        item = self._validate_type('directory')
        for name in item['content']:
            yield DictPath(self / name, filesystem=self._filesystem)

    def open(self, mode: str = 'r', encoding: Optional[str] = None, errors: Optional[str] = None) -> StringIO:
        """
        Open the file at the given path.

        Supported modes:
        - 'r', 'rt': Read text (default)

        Args:
            mode (str): Mode in which to open the file. Default is 'r'.
            encoding (str, optional): Encoding to use for text files.
            errors (str, optional): Error handling scheme for text files.

        Returns:
            StringIO: In-memory stream for text files.

        Raises:
            ValueError: If mode is not supported.
            TypeError: If the path is not a text file.
            FileNotFoundError: If the path does not exist.
        """
        valid_modes = {'r', 'rt'}
        if mode not in valid_modes:
            raise ValueError("Only read access for text files is supported (modes: 'r', 'rt')")

        item = self._validate_type('file')
        return StringIO(item['content'])

    def stat(self) -> os.stat_result:
        """
        Get the status of the file or directory at the given path.

        Returns:
            os.stat_result: An object containing the status of the file or directory.

        Raises:
            FileNotFoundError: If the path does not exist.
        """
        item = self._get_nested_item()
        metadata = item['metadata']
        st_mode = stat.S_IFDIR if item['type'] == 'directory' else stat.S_IFREG
        st_size = len(item['content']) if item['type'] == 'file' else 0

        return os.stat_result((
            st_mode,
            0,                          # st_ino
            0,                          # st_dev
            0,                          # st_nlink
            0,                          # st_uid
            0,                          # st_gid
            st_size,                    # st_size
            metadata['st_atime'],
            metadata['st_mtime'],
            metadata['st_ctime'],
        ))
