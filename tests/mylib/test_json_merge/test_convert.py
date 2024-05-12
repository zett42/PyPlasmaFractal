import pytest
from enum import Enum
from mylib.json_merge import handle_type_mismatch_gracefully

class Color(Enum):
    RED = 1
    GREEN = 2
    BLUE = 3

def test_str_to_enum():
    assert handle_type_mismatch_gracefully(Color.BLUE, "RED") == Color.RED
    assert handle_type_mismatch_gracefully(Color.RED, "YELLOW") == Color.RED
    # Test invalid Enum conversion: should return the target as default if source doesn't match any Enum member
    assert handle_type_mismatch_gracefully(Color.RED, "YELLOW") == Color.RED   

def test_enum_to_str():
    assert handle_type_mismatch_gracefully("unknown", Color.GREEN) == "GREEN"
    
def test_str_to_int():
    assert handle_type_mismatch_gracefully(456, "123") == 123

def test_int_to_str():
    assert handle_type_mismatch_gracefully("template", 789) == "789"

def test_str_to_float():
    assert handle_type_mismatch_gracefully(56.78, "12.34") == 12.34

def test_float_to_str():
    assert handle_type_mismatch_gracefully("float_string", 90.12) == "90.12"

def test_str_to_bool():
    assert handle_type_mismatch_gracefully(False, "true") is True
    assert handle_type_mismatch_gracefully(True, "false") is False
    assert handle_type_mismatch_gracefully(True, "maybe") is True

def test_bool_to_str():
    assert handle_type_mismatch_gracefully("false", True) == "True"
    assert handle_type_mismatch_gracefully("true", False) == "False"

def test_incompatible_types():
    assert handle_type_mismatch_gracefully([], {}) == []
    assert handle_type_mismatch_gracefully({}, 1.23) == {}

def test_invalid_conversion():
    assert handle_type_mismatch_gracefully(100, "not a number") == 100
