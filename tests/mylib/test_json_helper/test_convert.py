import pytest
from enum import Enum
from mylib.json_merge import convert_json_scalar

class Color(Enum):
    RED = 1
    GREEN = 2
    BLUE = 3

def test_str_to_enum():
    assert convert_json_scalar("RED", Color.BLUE) == Color.RED
    assert convert_json_scalar("YELLOW", Color.RED) == Color.RED
    # Test invalid Enum conversion: should return the target as default if source doesn't match any Enum member
    assert convert_json_scalar("YELLOW", Color.RED) == Color.RED   

def test_enum_to_str():
    assert convert_json_scalar(Color.GREEN, "unknown") == "GREEN"
    
def test_str_to_int():
    assert convert_json_scalar("123", 456) == 123

def test_int_to_str():
    assert convert_json_scalar(789, "template") == "789"

def test_str_to_float():
    assert convert_json_scalar("12.34", 56.78) == 12.34

def test_float_to_str():
    assert convert_json_scalar(90.12, "float_string") == "90.12"

def test_str_to_bool():
    assert convert_json_scalar("true", False) is True
    assert convert_json_scalar("false", True) is False
    assert convert_json_scalar("maybe", True) is True

def test_bool_to_str():
    assert convert_json_scalar(True, "false") == "True"
    assert convert_json_scalar(False, "true") == "False"

def test_incompatible_types():
    assert convert_json_scalar({}, []) == []
    assert convert_json_scalar(1.23, {}) == {}

def test_invalid_conversion():
    assert convert_json_scalar("not a number", 100) == 100
