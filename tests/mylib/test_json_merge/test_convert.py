import pytest
from enum import Enum
from mylib.json_merge import convert_json_scalar

class Color(Enum):
    RED = 1
    GREEN = 2
    BLUE = 3

def test_str_to_enum():
    assert convert_json_scalar(Color.BLUE, "RED") == Color.RED
    assert convert_json_scalar(Color.RED, "YELLOW") == Color.RED
    # Test invalid Enum conversion: should return the target as default if source doesn't match any Enum member
    assert convert_json_scalar(Color.RED, "YELLOW") == Color.RED   

def test_enum_to_str():
    assert convert_json_scalar("unknown", Color.GREEN) == "GREEN"
    
def test_str_to_int():
    assert convert_json_scalar(456, "123") == 123

def test_int_to_str():
    assert convert_json_scalar("template", 789) == "789"

def test_str_to_float():
    assert convert_json_scalar(56.78, "12.34") == 12.34

def test_float_to_str():
    assert convert_json_scalar("float_string", 90.12) == "90.12"

def test_str_to_bool():
    assert convert_json_scalar(False, "true") is True
    assert convert_json_scalar(True, "false") is False
    assert convert_json_scalar(True, "maybe") is True

def test_bool_to_str():
    assert convert_json_scalar("false", True) == "True"
    assert convert_json_scalar("true", False) == "False"

def test_incompatible_types():
    assert convert_json_scalar([], {}) == []
    assert convert_json_scalar({}, 1.23) == {}

def test_invalid_conversion():
    assert convert_json_scalar(100, "not a number") == 100
