import pytest
from unittest.mock import patch, MagicMock
from mylib.presets_manager import Preset, list_presets

def test_preset_instantiation():

    preset = Preset("config.json", True)
    assert preset.file_path == "config.json"
    assert preset.is_predefined is True


def test_list_presets_both_directories_exist():

    with patch('os.listdir') as mocked_listdir:

        mocked_listdir.side_effect = [
            ['app_preset1.json', 'app_preset2.json'],  # App directory files
            ['user_preset1.json', 'user_preset2.json']  # User directory files
        ]

        presets = list_presets('/fake/app_dir', '/fake/user_dir')

        expected_results = [
            ('app_preset1.json', True),
            ('app_preset2.json', True),
            ('user_preset1.json', False),
            ('user_preset2.json', False)
        ]

        assert len(presets) == 4
        assert all(isinstance(p, Preset) for p in presets)

        for preset, (expected_file, expected_predefined) in zip(presets, expected_results):
            assert preset.file_path == expected_file
            assert preset.is_predefined == expected_predefined


def test_list_presets_app_directory_missing():

    with patch('os.listdir') as mocked_listdir:

        mocked_listdir.side_effect = [FileNotFoundError, ['user_preset1.json']]

        presets = list_presets('/fake/app_dir', '/fake/user_dir')

        assert len(presets) == 1
        assert presets[0].file_path == 'user_preset1.json'
        assert presets[0].is_predefined == False


def test_list_presets_user_directory_missing():

    with patch('os.listdir') as mocked_listdir:

        mocked_listdir.side_effect = [['app_preset1.json'], FileNotFoundError]

        presets = list_presets('/fake/app_dir', '/fake/user_dir')

        assert len(presets) == 1
        assert presets[0].file_path == 'app_preset1.json'
        assert presets[0].is_predefined == True


def test_list_presets_no_json_files():

    with patch('os.listdir') as mocked_listdir:

        mocked_listdir.side_effect = [
            ['app_preset1.txt', 'app_preset2.doc'],  # Non-JSON files in app directory
            ['user_preset1.txt', 'user_preset2.doc']  # Non-JSON files in user directory
        ]
        presets = list_presets('/fake/app_dir', '/fake/user_dir')

        assert len(presets) == 0

