from typing import List, Hashable, Dict
import fnmatch
from PyPlasmaFractal.mylib.config.storage import Storage

class FunctionParam:
    """
    Information about a parameter used in functions and how to represent it in the UI.
    """
    def __init__(self, display_name: str, min: float = 0.0, max: float = 1.0, logarithmic: bool = False, default: float = 0.0):
        self.display_name = display_name
        self.min = min
        self.max = max
        self.logarithmic = logarithmic
        self.default = default

class FunctionInfo:
    """
    Contains information about a function, including its parameters.
    """
    def __init__(self, display_name: str, params: List[FunctionParam]):
        self.display_name = display_name
        self.params = params

class FunctionRegistryDynamic:
    """
    A class for storing and managing function informations.
    """
    def __init__(self, storage: Storage, data_name: str = "*"):
        self.storage = storage
        self.data_name = data_name
        self.functions = {}
        self.load(data_name, merge=False)

    def load(self, data_name: str = None, merge: bool = False):
        """
        Load functions from the storage that match the specified data name pattern.
        If no pattern is specified, use the data name from the instance.
        If merge is False, clear existing functions before loading.
        """
        if data_name is None:
            data_name = self.data_name

        if not merge:
            self.clear()

        # List all data names from the storage
        all_data_names = self.storage.list()

        # Filter data names based on the pattern
        matched_data_names = fnmatch.filter(all_data_names, data_name)

        # Load and merge functions from all matched data names
        for name in matched_data_names:
            data = self.storage.load(name)
            self._merge_functions(data["functions"])

    def clear(self):
        """
        Clear the existing functions.
        """
        self.functions = {}

    def _merge_functions(self, new_functions: Dict[str, Dict]):
        """
        Merge a new set of functions into the existing functions dictionary.
        Raise an exception if a function key already exists.
        """
        for key, info in new_functions.items():
            if key in self.functions:
                raise KeyError(f"Function key '{key}' already exists in the registry.")
            params = [
                FunctionParam(
                    param["name"],
                    param.get("min", 0.0),
                    param.get("max", 1.0),
                    param.get("logarithmic", False),
                    param.get("default", 0.0)
                ) for param in info["params"]
            ]
            self.functions[key] = FunctionInfo(info["display_name"], params)

    def has_function(self, key: Hashable) -> bool:
        """
        Check if a function with a given name exists in the registry.
        """
        return key in self.functions
    
    def get_function_info(self, key: Hashable) -> FunctionInfo:
        """
        Retrieve the function info for a given function name.
        """
        return self.functions[key]
    
    def get_function_keys(self) -> List[str]:
        """
        Retrieve a list of all function names in the registry.
        """
        return list(self.functions.keys())

    def max_param_count(self) -> int:
        """
        Compute the maximum number of parameters among all functions in the registry.
        """
        return max(len(info.params) for info in self.functions.values())

    def get_all_param_defaults(self) -> Dict[str, List[float]]:
        """
        Retrieve default parameters for all functions in the registry.
        This method converts enum keys to string representations if use_string_keys is True.
        Assumes each function conforms to having 'params' with 'default' attributes.
        """
        return {
            key: [param.default for param in info.params] 
            for key, info in self.functions.items()
        }
