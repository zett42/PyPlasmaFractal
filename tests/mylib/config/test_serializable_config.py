import pytest
from PyPlasmaFractal.mylib.config.serializable_config import SerializableConfig


class SimpleConfig(SerializableConfig):
    def __init__(self):
        super().__init__()
        self.name = "test"
        self.value = 42
        self._private = "hidden"


class NestedConfig(SerializableConfig):
    def __init__(self):
        super().__init__()
        self.name = "parent"
        self.child = SimpleConfig()
        self._private = "hidden"


@pytest.fixture
def simple_config():
    return SimpleConfig()


@pytest.fixture
def nested_config():
    return NestedConfig()


def test_to_dict_simple(simple_config):
    """Test basic serialization of simple attributes"""
    result = simple_config.to_dict()
    assert result == {"name": "test", "value": 42}
    assert "_private" not in result


def test_to_dict_nested(nested_config):
    """Test serialization with nested objects and type conversion"""
    result = nested_config.to_dict()
    
    # Verify the result and nested objects are plain dicts
    assert type(result) == dict
    assert type(result["child"]) == dict
    
    # Verify content
    assert result["name"] == "parent"
    assert result["child"]["name"] == "test"
    assert result["child"]["value"] == 42
    assert "_private" not in result


def test_merge_dict_simple(simple_config):
    """Test merging new values into simple config"""
    simple_config.merge_dict({"name": "modified", "value": 99, "invalid": "ignored"})
    assert simple_config.name == "modified"
    assert simple_config.value == 99
    assert not hasattr(simple_config, "invalid")


def test_merge_dict_nested(nested_config):
    """Test merging with nested configurations"""
    nested_config.merge_dict({
        "name": "modified_parent",
        "child": {
            "name": "modified_child",
            "value": 100
        }
    })
    assert nested_config.name == "modified_parent"
    assert nested_config.child.name == "modified_child"
    assert nested_config.child.value == 100


def test_merge_type_mismatch(simple_config):
    """Test graceful handling of type mismatches during merge"""
    simple_config.merge_dict({
        "name": 123,  # Should be converted to string
        "value": "99"  # Should be converted to int
    })
    assert isinstance(simple_config.name, str)
    assert isinstance(simple_config.value, int)


def test_merge_nonexistent_attributes(simple_config):
    """Test that merging non-existent attributes are ignored"""
    original_dict = simple_config.to_dict()
    simple_config.merge_dict({"new_field": "value"})
    assert simple_config.to_dict() == original_dict


class ListConfig(SerializableConfig):
    def __init__(self):
        super().__init__()
        # All lists maintain their size during merging for data migration compatibility
        self.numbers = [1, 2, 3]
        self.params = [{"value": 0.5}, {"value": 1.0}]


@pytest.fixture
def list_config():
    return ListConfig()


def test_list_serialization(list_config):
    """Test serialization of lists and nested structures"""
    result = list_config.to_dict()
    assert result["numbers"] == [1, 2, 3]
    assert result["params"] == [{"value": 0.5}, {"value": 1.0}]


def test_list_merge(list_config):
    """Test merging of lists in config"""
    list_config.merge_dict({
        "numbers": [4, 5, 6],
        "params": [{"value": 0.7}, {"value": 0.8}]
    })
    assert list_config.numbers == [4, 5, 6]
    assert list_config.params == [{"value": 0.7}, {"value": 0.8}]


def test_list_merge_incoming_shorter(list_config):
    """Test merging when incoming data has shorter lists - size should be preserved"""
    incoming_data = {
        "numbers": [9, 8],        # Two elements merged into three-element list
        "params": [{"value": 0.7}] # One element merged into two-element list
    }
    list_config.merge_dict(incoming_data)
    
    # List sizes are preserved, with remaining elements keeping their original values
    assert list_config.numbers == [9, 8, 3]
    assert list_config.params == [{"value": 0.7}, {"value": 1.0}]


def test_list_merge_incoming_longer(list_config):
    """Test merging when incoming data has longer lists - extra elements should be ignored"""
    incoming_data = {
        "numbers": [9, 8, 7, 6],        # Four elements truncated to three
        "params": [{"value": 0.7}, {"value": 0.8}, {"value": 0.9}]  # Three elements truncated to two
    }
    list_config.merge_dict(incoming_data)
    
    # List sizes are preserved by ignoring extra elements
    assert list_config.numbers == [9, 8, 7]
    assert list_config.params == [{"value": 0.7}, {"value": 0.8}]
