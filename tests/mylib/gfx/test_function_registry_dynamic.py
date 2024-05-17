import pytest
from PyPlasmaFractal.mylib.gfx.function_registry_dynamic import FunctionRegistryDynamic
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

# Create a fixture for mock storage
@pytest.fixture
def mock_storage():
    storage = MockStorage()

    initial_data = {
        "description": "A set of example feedback blend functions",
        "functions": {
            "ExampleSingleParam": {
                "display_name": "Example Single Param",
                "params": [
                    {
                        "name": "Single Param",
                        "logarithmic": False,
                        "min": 0.0,
                        "max": 1.0,
                        "default": 0.1
                    }
                ]
            },
            "ExampleTwoParams": {
                "display_name": "Example Two Params",
                "params": [
                    {
                        "name": "First Param",
                        "logarithmic": False,
                        "min": 0.0,
                        "max": 1.0,
                        "default": 0.2
                    },
                    {
                        "name": "Second Param",
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
                "params": [
                    {
                        "name": "New Param",
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
                "params": [
                    {
                        "name": "Duplicate Param",
                        "logarithmic": False,
                        "min": 0.0,
                        "max": 1.0,
                        "default": 0.3
                    }
                ]
            }
        }
    }

    storage.save(initial_data, "initial_data")
    storage.save(new_data, "new_data")
    storage.save(duplicate_data, "duplicate_data")

    return storage


def test_initialization(mock_storage):
    
    registry = FunctionRegistryDynamic(mock_storage, "initial_data")
    assert registry.data_name == "initial_data"
    assert len(registry.functions) == 2


def test_has_function(mock_storage):
    
    registry = FunctionRegistryDynamic(mock_storage, "initial_data")
    assert registry.has_function("ExampleSingleParam")
    assert not registry.has_function("NonExistentFunction")


def test_get_function_info(mock_storage):
    
    registry = FunctionRegistryDynamic(mock_storage, "initial_data")
    
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
    registry = FunctionRegistryDynamic(mock_storage, "initial_data")
    
    keys = registry.get_all_function_keys()
    assert set(keys) == {"ExampleSingleParam", "ExampleTwoParams"}


def test_max_param_count(mock_storage):
    
    registry = FunctionRegistryDynamic(mock_storage, "initial_data")
    
    assert registry.max_param_count() == 2


def test_get_all_param_defaults(mock_storage):
    
    registry = FunctionRegistryDynamic(mock_storage, "initial_data")
    
    defaults = registry.get_all_param_defaults()
    assert defaults == {
        "ExampleSingleParam": [0.1],
        "ExampleTwoParams": [0.2, 1.0]
    }


def test_load_with_merge(mock_storage):
    
    registry = FunctionRegistryDynamic(mock_storage, "initial_data")
    registry.load("new_data", merge=True)

    assert len(registry.functions) == 3
    assert "NewFunction" in registry.functions
    
    new_function_info = registry.get_function_info("NewFunction")
    
    assert new_function_info.display_name == "New Function"
    assert len(new_function_info.params) == 1
    assert new_function_info.params[0].default == 0.05


def test_load_without_merge(mock_storage):
    
    registry = FunctionRegistryDynamic(mock_storage, "initial_data")
    registry.load("new_data")

    assert len(registry.functions) == 1
    assert "NewFunction" in registry.functions
    
    new_function_info = registry.get_function_info("NewFunction")
    
    assert new_function_info.display_name == "New Function"
    assert len(new_function_info.params) == 1
    assert new_function_info.params[0].default == 0.05


def test_clear(mock_storage):
    
    registry = FunctionRegistryDynamic(mock_storage, "initial_data")
    registry.clear()
    
    assert len(registry.functions) == 0


def test_load_duplicate_key(mock_storage):
    
    registry = FunctionRegistryDynamic(mock_storage, "initial_data")
    with pytest.raises(KeyError, match="Function key 'ExampleSingleParam' already exists in the registry."):
        registry.load("duplicate_data", merge=True)
