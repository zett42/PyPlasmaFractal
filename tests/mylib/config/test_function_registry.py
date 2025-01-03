import pytest
from PyPlasmaFractal.mylib.config.function_info import ColorParamType, FloatParamType
from PyPlasmaFractal.mylib.config.function_registry import FunctionRegistry, ParamType
from PyPlasmaFractal.mylib.config.storage import Storage

# Create a mock Storage class
class MockStorage(Storage):
    def __init__(self):
        self.storage = {}

    def save(self, data: dict, name: str) -> None:
        self.storage[name] = data

    def load(self, name: str) -> dict:
        return self.storage.get(name, {})

    def delete(self, name: str) -> None:
        if name in self.storage:
            del self.storage[name]

    def list(self) -> list:
        return list(self.storage.keys())

    def exists(self, name: str) -> bool:
        return name in self.storage

    def get_full_path(self, name: str) -> str:
        return f"/mock/path/{name}"

# Create a fixture for mock storage
@pytest.fixture
def mock_storage():
    storage = MockStorage()

    initial_data = {
        "description": "A set of example feedback blend functions",
        "functions": {
            "ExampleSingleParam": {
                "display_name": "Example Single Param",
                "description": "Description for Example Single Param",
                "params": [
                    {
                        "name": "single_param",
                        "display_name": "Single Param",
                        "param_type": "float",
                        "logarithmic": False,
                        "min": 0.0,
                        "max": 1.0,
                        "default": 0.1
                    }
                ]
            },
            "ExampleTwoParams": {
                "display_name": "Example Two Params",
                "description": "Description for Example Two Params",
                "params": [
                    {
                        "name": "first_param",
                        "display_name": "First Param",
                        "param_type": "float",
                        "logarithmic": False,
                        "min": 0.0,
                        "max": 1.0,
                        "default": 0.2
                    },
                    {
                        "name": "second_param",
                        "display_name": "Second Param",
                        "param_type": "float",
                        "logarithmic": True,
                        "min": 0.0,
                        "max": 2.0,
                        "default": 1.0
                    }
                ]
            }
        }
    }

    new_data = {
        "description": "A new set of feedback blend functions",
        "functions": {
            "NewFunction": {
                "display_name": "New Function",
                "description": "Description for New Function",
                "params": [
                    {
                        "name": "new_param",
                        "display_name": "New Param",
                        "param_type": "float",
                        "logarithmic": True,
                        "min": 0.0,
                        "max": 1.0,
                        "default": 0.05
                    }
                ]
            }
        }
    }

    duplicate_data = {
        "description": "Duplicate function keys",
        "functions": {
            "ExampleSingleParam": {
                "display_name": "Duplicate Example Single Param",
                "description": "Description for Duplicate Example Single Param",
                "params": [
                    {
                        "name": "duplicate_param",
                        "display_name": "Duplicate Param",
                        "param_type": "float",
                        "logarithmic": False,
                        "min": 0.0,
                        "max": 1.0,
                        "default": 0.3
                    }
                ]
            }
        }
    }

    float_data = {
        "description": "Test float parameter",
        "functions": {
            "FloatFunction": {
                "display_name": "Float Function",
                "description": "Function with float parameter",
                "params": [
                    {
                        "name": "float_param",
                        "display_name": "Float Param",
                        "param_type": "float",
                        "min": 0.0,
                        "max": 1.0,
                        "default": 0.5
                    }
                ]
            }
        }
    }

    color_data = {
        "description": "Test color parameter",
        "functions": {
            "ColorFunction": {
                "display_name": "Color Function",
                "description": "Function with color parameter",
                "params": [
                    {
                        "name": "color_param",
                        "display_name": "Color Param",
                        "param_type": "color",
                        "default": [1.0, 0.2, 0.5, 0.9]
                    }
                ]
            }
        }
    }

    invalid_float_data = {
        "description": "Invalid float parameter",
        "functions": {
            "InvalidFloatFunction": {
                "display_name": "Invalid Float Function",
                "description": "Function with invalid float parameter",
                "params": [
                    {
                        "name": "invalid_float_param",
                        "display_name": "Invalid Float Param",
                        "param_type": "float",
                        "min": 0.0,
                        "max": 1.0,
                        "default": "not a float"
                    }
                ]
            }
        }
    }

    invalid_color_data = {
        "description": "Invalid color parameter",
        "functions": {
            "InvalidColorFunction": {
                "display_name": "Invalid Color Function",
                "description": "Function with invalid color parameter",
                "params": [
                    {
                        "name": "invalid_color_param",
                        "display_name": "Invalid Color Param",
                        "param_type": "color",
                        "default": [1.0, 0.5]  # Invalid: only 2 components instead of 3 or 4
                    }
                ]
            }
        }
    }

    storage.save(initial_data, "initial_data")
    storage.save(new_data, "new_data")
    storage.save(duplicate_data, "duplicate_data")
    storage.save(float_data, "float_data")
    storage.save(color_data, "color_data")
    storage.save(invalid_float_data, "invalid_float_data")
    storage.save(invalid_color_data, "invalid_color_data")

    return storage


def test_initialization(mock_storage):
    
    registry = FunctionRegistry(mock_storage, "initial_data")
    assert registry.name_filter == "initial_data"
    assert len(registry.functions) == 2


def test_has_function(mock_storage):
    
    registry = FunctionRegistry(mock_storage, "initial_data")
    assert registry.has_function("ExampleSingleParam")
    assert not registry.has_function("NonExistentFunction")


def test_get_function_info(mock_storage):
    
    registry = FunctionRegistry(mock_storage, "initial_data")
    
    single_param_info = registry.get_function_info("ExampleSingleParam")
    assert single_param_info.display_name == "Example Single Param"
    assert len(single_param_info.params) == 1
    assert single_param_info.params[0].display_name == "Single Param"

    two_params_info = registry.get_function_info("ExampleTwoParams")
    assert two_params_info.display_name == "Example Two Params"
    assert len(two_params_info.params) == 2
    assert two_params_info.params[0].display_name == "First Param"
    assert two_params_info.params[1].display_name == "Second Param"


def test_get_all_function_keys(mock_storage):
    registry = FunctionRegistry(mock_storage, "initial_data")
    
    keys = registry.get_function_keys()
    assert set(keys) == {"ExampleSingleParam", "ExampleTwoParams"}


def test_get_all_param_defaults(mock_storage):
    
    registry = FunctionRegistry(mock_storage, "initial_data")
    
    defaults = registry.get_all_param_defaults()
    assert defaults == {
        "ExampleSingleParam": {"single_param": 0.1},
        "ExampleTwoParams": {"first_param": 0.2, "second_param": 1.0}
    }


def test_load_with_merge(mock_storage):
    
    registry = FunctionRegistry(mock_storage, "initial_data")
    registry.load("new_data", merge=True)

    assert len(registry.functions) == 3
    assert "NewFunction" in registry.functions
    
    new_function_info = registry.get_function_info("NewFunction")
    
    assert new_function_info.display_name == "New Function"
    assert len(new_function_info.params) == 1
    assert new_function_info.params[0].default == 0.05


def test_load_without_merge(mock_storage):
    
    registry = FunctionRegistry(mock_storage, "initial_data")
    registry.load("new_data")

    assert len(registry.functions) == 1
    assert "NewFunction" in registry.functions
    
    new_function_info = registry.get_function_info("NewFunction")
    
    assert new_function_info.display_name == "New Function"
    assert len(new_function_info.params) == 1
    assert new_function_info.params[0].default == 0.05


def test_clear(mock_storage):
    
    registry = FunctionRegistry(mock_storage, "initial_data")
    registry.clear()
    
    assert len(registry.functions) == 0


def test_load_duplicate_key(mock_storage):
    
    registry = FunctionRegistry(mock_storage, "initial_data")
    with pytest.raises(KeyError, match="Function key 'ExampleSingleParam' already exists in the registry."):
        registry.load("duplicate_data", merge=True)

def test_float_param(mock_storage):
    registry = FunctionRegistry(mock_storage, "float_data")
    
    float_function_info = registry.get_function_info("FloatFunction")
    assert float_function_info.display_name == "Float Function"
    assert len(float_function_info.params) == 1
    assert float_function_info.params[0].display_name == "Float Param"
    assert float_function_info.params[0].min == 0.0
    assert float_function_info.params[0].max == 1.0
    assert float_function_info.params[0].default == 0.5
    assert isinstance(float_function_info.params[0].param_type, FloatParamType)

def test_color_param(mock_storage):
    registry = FunctionRegistry(mock_storage, "color_data")
    
    color_function_info = registry.get_function_info("ColorFunction")
    assert color_function_info.display_name == "Color Function"
    assert len(color_function_info.params) == 1
    assert color_function_info.params[0].display_name == "Color Param"
    assert color_function_info.params[0].default == [1.0, 0.2, 0.5, 0.9]
    assert isinstance(color_function_info.params[0].param_type, ColorParamType)

def test_invalid_float_param(mock_storage):
    with pytest.raises(RuntimeError, match="Error processing function key 'InvalidFloatFunction': Failed to convert default value for parameter 'invalid_float_param': Cannot convert not a float to float"):
        FunctionRegistry(mock_storage, "invalid_float_data")

def test_invalid_color_param(mock_storage):
    with pytest.raises(RuntimeError, match="Error processing function key 'InvalidColorFunction': Failed to convert default value for parameter 'invalid_color_param': Color must have 3 or 4 components"):
        FunctionRegistry(mock_storage, "invalid_color_data")
