import os
import pytest
import json
from unittest.mock import mock_open, patch
from mylib.config_file_manager import ConfigFileManager

# Test setup
@pytest.fixture
def config_manager():
    return ConfigFileManager(app_name="TestApp", app_author="TestAuthor")

@pytest.fixture
def config_object():
    return {
        'key1': 'value1',
        'key2': 'value2',
        'key3': 'value3'
    }

# Test default serialization
def test_default_save(config_manager):

    obj = {'key': 'value'}
    serialized_data = ConfigFileManager._default_save(obj)
    assert serialized_data == json.dumps(obj, indent=4), "Serialization should match JSON dumps with indent"


# Test default deserialization
def test_default_load(config_manager):

    json_str = '{"key": "value"}'
    obj = ConfigFileManager._default_load(json_str)
    assert obj == json.loads(json_str), "Deserialization should match JSON loads"


# Test saving configuration
def test_save_config(config_manager, config_object, mocker):

    mocker.patch('os.path.exists', return_value=True)
    mock_file_open = mock_open()
    mocker.patch('builtins.open', mock_file_open)

    expected_file_path = os.path.join(config_manager.directory, config_manager.default_filename)

    config_manager.save_config(config_object)

    # Using the expected_file_path which accounts for path separators
    mock_file_open.assert_called_once_with(expected_file_path, 'w', encoding='utf-8')
    mock_file_open().write.assert_called_once_with(json.dumps(config_object, indent=4))


# Test loading configuration
def test_load_config(config_manager, mocker):

    mocker.patch('os.path.exists', return_value=True)
    config_data = '{"key": "value"}'
    mock_file_open = mock_open(read_data=config_data)
    mocker.patch('builtins.open', mock_file_open)

    expected_file_path = os.path.join(config_manager.directory, config_manager.default_filename)

    loaded_config = config_manager.load_config()

    # Using the expected_file_path which accounts for path separators
    mock_file_open.assert_called_once_with(expected_file_path, 'r', encoding='utf-8')
    assert loaded_config == json.loads(config_data), "Loaded config should match the expected JSON object"


# Test file not found error
def test_load_config_file_not_found(config_manager, mocker):

    mocker.patch('os.path.exists', return_value=False)

    with pytest.raises(FileNotFoundError):
        config_manager.load_config(must_exist=True)


# Test custom filename specified in constructor
def test_custom_filename_through_constructor(config_manager, mocker):

    # Specify a custom filename in the constructor
    custom_filename = "custom_config.json"
    custom_config_manager = ConfigFileManager(app_name="TestApp", app_author="TestAuthor", filename=custom_filename)

    # Mock dependencies for file operations
    mocker.patch('os.path.exists', return_value=True)
    config_data = '{"key": "value"}'
    mock_file_open = mock_open(read_data=config_data)
    mocker.patch('builtins.open', mock_file_open)

    # Test saving configuration with the default filename set in constructor
    custom_config_manager.save_config({'key': 'value'})

    # Constructing the expected file path with the constructor-specified filename
    expected_file_path = os.path.join(custom_config_manager.directory, custom_filename)

    # Asserting that the file is opened with the correct path and mode for saving
    mock_file_open.assert_called_with(expected_file_path, 'w', encoding='utf-8')

    # Test loading configuration with the default filename set in constructor
    loaded_config = custom_config_manager.load_config()

    # Asserting that the file is opened with the correct path and mode for loading
    mock_file_open.assert_called_with(expected_file_path, 'r', encoding='utf-8')

    # Asserting that the loaded configuration matches the expected JSON object
    assert loaded_config == json.loads(config_data), "Loaded config should match the expected JSON object"


# Test saving configuration with custom filename
def test_save_config_with_custom_filename(config_manager, config_object, mocker):

    custom_filename = "custom_config.json"
    mocker.patch('os.path.exists', return_value=True)
    mock_file_open = mock_open()
    mocker.patch('builtins.open', mock_file_open)

    # Using a custom filename
    config_manager.save_config(config_object, filename=custom_filename)

    # Constructing the expected file path with custom filename
    expected_file_path = os.path.join(config_manager.directory, custom_filename)

    # Asserting that the file is opened with the correct path and mode
    mock_file_open.assert_called_once_with(expected_file_path, 'w', encoding='utf-8')
    # Asserting that the content written to the file is correct
    mock_file_open().write.assert_called_once_with(json.dumps(config_object, indent=4))


# Test loading configuration with custom filename
def test_load_config_with_custom_filename(config_manager, mocker):

    custom_filename = "custom_config.json"
    mocker.patch('os.path.exists', return_value=True)
    config_data = '{"key": "value"}'
    mock_file_open = mock_open(read_data=config_data)
    mocker.patch('builtins.open', mock_file_open)

    # Using a custom filename
    loaded_config = config_manager.load_config(filename=custom_filename)

    # Constructing the expected file path with custom filename
    expected_file_path = os.path.join(config_manager.directory, custom_filename)

    # Asserting that the file is opened with the correct path and mode
    mock_file_open.assert_called_once_with(expected_file_path, 'r', encoding='utf-8')
    # Asserting that the loaded configuration matches the expected JSON object
    assert loaded_config == json.loads(config_data), "Loaded config should match the expected JSON object"
