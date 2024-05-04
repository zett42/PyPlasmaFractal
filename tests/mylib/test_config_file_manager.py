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


def test_default_initialization(mocker):
    # Mock appdirs to return a specific default path
    default_dir = "/default/path"
    mocker.patch('mylib.config_file_manager.user_data_dir', return_value=default_dir)
    mocker.patch('mylib.config_file_manager.site_data_dir', return_value=default_dir)

    # Initialize without parameters
    config_manager = ConfigFileManager()

    # Check if it defaults to the mocked directory
    assert config_manager.directory == default_dir, "Should default to a predefined directory when app details are missing"
    
    # Verify default filename is set
    assert config_manager.default_filename == 'config.json', "Should default to 'config.json' if filename is not provided"

    # Verify default save and load functions are used
    assert config_manager.save_function.__name__ == '_default_save', "Should use the default save function when none is provided"
    assert config_manager.load_function.__name__ == '_default_load', "Should use the default load function when none is provided"


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


# Test initialization with an explicit directory
def test_explicit_directory():

    directory = "/explicit/directory"
    config_manager = ConfigFileManager(directory=directory)

    assert config_manager.directory == directory, "Should use the explicitly provided directory"

# Test default directory usage
def test_default_directory_usage(mocker):

    user_dir = "/user/default/dir"
    site_dir = "/site/default/dir"

    mocker.patch('mylib.config_file_manager.user_data_dir', return_value=user_dir)
    mocker.patch('mylib.config_file_manager.site_data_dir', return_value=site_dir)

    # Test using user directory
    config_manager_user = ConfigFileManager(app_name="TestApp", app_author="TestAuthor", use_user_dir=True)
    assert config_manager_user.directory == user_dir, "Should default to user directory"

    # Test using site directory
    config_manager_site = ConfigFileManager(app_name="TestApp", app_author="TestAuthor", use_user_dir=False)
    assert config_manager_site.directory == site_dir, "Should default to site directory"


# Test subdirectory handling
def test_subdirectory_handling():

    directory = "/base/directory"
    sub_dir = "sub/directory"

    config_manager = ConfigFileManager(directory=directory, sub_dir=sub_dir)

    expected_path = os.path.join(directory, sub_dir)

    assert config_manager.directory == expected_path, "Should correctly append the subdirectory"


# Test custom save and load functions
def test_custom_save_and_load_functions():

    custom_save = lambda x: x
    custom_load = lambda x: x

    config_manager = ConfigFileManager(save_function=custom_save, load_function=custom_load)

    assert config_manager.save_function is custom_save, "Should use the custom save function"
    assert config_manager.load_function is custom_load, "Should use the custom load function"
