import pytest
import tempfile
from pathlib import Path
from PyPlasmaFractal.mylib.config.dict_text_storage import DictTextFileStorage
from PyPlasmaFractal.mylib.config.storage import *

@pytest.fixture
def storage():
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create some sample text files in the temporary directory
        files = {
            "file1.txt": "Content of file 1",
            "file2.txt": "Content of file 2",
            "subdir/file3.txt": "Content of file 3"
        }
        for filename, content in files.items():
            file_path = Path(temp_dir) / filename
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w') as f:
                f.write(content)
        
        storage = DictTextFileStorage(temp_dir)
        yield storage


def test_load_from_directory(storage):
    
    assert storage.exists("file1.txt")
    assert storage.exists("file2.txt")
    assert storage.exists("subdir/file3.txt")
    assert not storage.exists("nonexistent.txt")


def test_load_from_directory_non_recursive():
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create some sample text files in the temporary directory
        files = {
            "file1.txt": "Content of file 1",
            "file2.txt": "Content of file 2",
            "subdir/file3.txt": "Content of file 3"
        }
        for filename, content in files.items():
            file_path = Path(temp_dir) / filename
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w') as f:
                f.write(content)
        
        storage = DictTextFileStorage(temp_dir, recurse=False)
        files = storage.list()
        
        assert "file1.txt" in files
        assert "file2.txt" in files
        assert "subdir/file3.txt" not in files
        

def test_save_and_load(storage):
    
    storage.save("New content", "newfile.txt")
    assert storage.load("newfile.txt") == "New content"


def test_load_nonexistent_file(storage):
    
    with pytest.raises(StorageItemNotFoundError):
        storage.load("nonexistent.txt")


def test_delete_file(storage):
    
    storage.delete("file1.txt")
    assert not storage.exists("file1.txt")
    with pytest.raises(StorageItemNotFoundError):
        storage.delete("file1.txt")


def test_list_files(storage):
    
    files = storage.list()
    assert "file1.txt" in files
    assert "file2.txt" in files
    assert "subdir/file3.txt" in files


def test_custom_pattern():
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create some sample text files in the temporary directory
        files = {
            "file1.txt": "Content of file 1",
            "file2.txt": "Content of file 2",
            "file3.shader": "Content of file 3"
        }
        for filename, content in files.items():
            file_path = Path(temp_dir) / filename
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w') as f:
                f.write(content)
        
        storage = DictTextFileStorage(temp_dir, '*.shader')
        files = storage.list()
        
        assert "file3.shader" in files
        assert "file1.txt" not in files
        assert "file2.txt" not in files


def test_load_from_empty_directory():
    
    with tempfile.TemporaryDirectory() as temp_dir:
        storage = DictTextFileStorage(temp_dir)
        files = storage.list()
        assert files == []
