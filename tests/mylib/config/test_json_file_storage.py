import json
from unittest.mock import patch
import pytest
from pathlib import Path

from mylib.config.storage import *
from mylib.config.json_file_storage import *

@pytest.fixture
def temp_storage(tmp_path):
    
    return JsonFileStorage(str(tmp_path))


def test_init_storage_success(tmp_path):
    
    storage = JsonFileStorage(str(tmp_path))
    assert storage.directory == tmp_path
    assert storage.directory.exists()


def test_init_storage_failure(monkeypatch):
    
    def mock_mkdir(self, parents=True, exist_ok=True):
        raise OSError("Cannot create directory")
    
    monkeypatch.setattr(Path, "mkdir", mock_mkdir)
    
    with pytest.raises(StorageCreateDirectoryError):
        JsonFileStorage("/invalid/dir")


def test_save_json(temp_storage):
    
    data = {"key": "value"}
    filename = "test.json"
    
    temp_storage.save(data, filename)
    saved_path = temp_storage.directory / filename
    assert saved_path.exists()
    
    with saved_path.open('r') as file:
        loaded_data = json.load(file)
    assert loaded_data == data


def test_load_json_success(temp_storage):
    
    data = {"key": "value"}
    filename = "test.json"
    
    temp_storage.save(data, filename)
    loaded_data = temp_storage.load(filename)
    assert loaded_data == data


def test_load_json_not_found(temp_storage):
    
    with pytest.raises(StorageItemNotFoundError):
        temp_storage.load("nonexistent.json")


def test_load_json_invalid(temp_storage, tmp_path):
    
    invalid_json = tmp_path / "invalid.json"
    with invalid_json.open('w') as file:
        file.write("{invalid json}")
    
    with pytest.raises(StorageItemLoadError):
        temp_storage.load(invalid_json.name)


def test_delete_json_success(temp_storage):
    
    data = {"key": "value"}
    filename = "test.json"
    
    temp_storage.save(data, filename)
    temp_storage.delete(filename)
    
    with pytest.raises(StorageItemNotFoundError):
        temp_storage.load(filename)


def test_delete_json_not_found(temp_storage):
    
    with pytest.raises(StorageItemNotFoundError):
        temp_storage.delete("nonexistent.json")


def test_list_json_files(temp_storage):
    
    filenames = ["file1.json", "file2.json", "file3.json"]
    for filename in filenames:
        temp_storage.save({"key": "value"}, filename)
    
    listed_files = temp_storage.list()
    assert sorted(listed_files) == sorted(filenames)


@patch.object(Path, 'glob', side_effect=OSError("Cannot list files"))
def test_list_json_files_failure(mock_glob, temp_storage):
    with pytest.raises(StorageItemListingError):
        temp_storage.list()