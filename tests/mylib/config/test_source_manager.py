import pytest
from unittest.mock import MagicMock
from PyPlasmaFractal.mylib.config.storage import Storage
from PyPlasmaFractal.mylib.config.source_manager import StorageSourceManager


@pytest.fixture
def mock_app_storage():
    
    mock_storage = MagicMock(spec=Storage)
    mock_storage.list.return_value = ['app_item1', 'app_item2']
    return mock_storage


@pytest.fixture
def mock_user_storage():
    
    mock_storage = MagicMock(spec=Storage)
    mock_storage.list.return_value = ['user_item1', 'user_item2']
    return mock_storage


@pytest.fixture
def storage_source_manager(mock_app_storage, mock_user_storage):
    return StorageSourceManager(app_storage=mock_app_storage, user_storage=mock_user_storage)


def test_initialization(storage_source_manager, mock_app_storage, mock_user_storage):
    
    assert storage_source_manager.app_storage == mock_app_storage
    assert storage_source_manager.user_storage == mock_user_storage


def test_list_items(storage_source_manager, mock_app_storage, mock_user_storage):
    
    items = storage_source_manager.list()

    assert len(items) == 4
    assert items[0] == StorageSourceManager.Item(name='app_item1', storage=mock_app_storage)
    assert items[1] == StorageSourceManager.Item(name='app_item2', storage=mock_app_storage)
    assert items[2] == StorageSourceManager.Item(name='user_item1', storage=mock_user_storage)
    assert items[3] == StorageSourceManager.Item(name='user_item2', storage=mock_user_storage)


def test_list_items_empty_storage():
    
    mock_app_storage = MagicMock(spec=Storage)
    mock_app_storage.list.return_value = []

    mock_user_storage = MagicMock(spec=Storage)
    mock_user_storage.list.return_value = []

    storage_source_manager = StorageSourceManager(app_storage=mock_app_storage, user_storage=mock_user_storage)
    items = storage_source_manager.list()

    assert items == []


def test_list_items_only_app_storage():
    
    mock_app_storage = MagicMock(spec=Storage)
    mock_app_storage.list.return_value = ['app_item1']

    mock_user_storage = MagicMock(spec=Storage)
    mock_user_storage.list.return_value = []

    storage_source_manager = StorageSourceManager(app_storage=mock_app_storage, user_storage=mock_user_storage)
    items = storage_source_manager.list()

    assert len(items) == 1
    assert items[0] == StorageSourceManager.Item(name='app_item1', storage=mock_app_storage)


def test_list_items_only_user_storage():
    
    mock_app_storage = MagicMock(spec=Storage)
    mock_app_storage.list.return_value = []

    mock_user_storage = MagicMock(spec=Storage)
    mock_user_storage.list.return_value = ['user_item1']

    storage_source_manager = StorageSourceManager(app_storage=mock_app_storage, user_storage=mock_user_storage)
    items = storage_source_manager.list()

    assert len(items) == 1
    assert items[0] == StorageSourceManager.Item(name='user_item1', storage=mock_user_storage)
