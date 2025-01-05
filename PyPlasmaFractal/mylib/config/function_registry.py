from typing import List, Hashable, Dict, Any
import fnmatch
from PyPlasmaFractal.mylib.config.function_info import FunctionInfo, ParamType, ColorParamType, FloatParamType, IntParamType
from PyPlasmaFractal.mylib.config.storage import Storage

class FunctionRegistry:
    """
    A class for storing and managing function information.
    """
    
    DEFAULT_PARAM_TYPES = [
        IntParamType(),
        FloatParamType(),
        ColorParamType()
    ]
    
    def __init__(self, storage: Storage, name_filter: str = "*", param_types: List[ParamType] = None, category: str = None):
        """
        Initialize the FunctionRegistry instance.

        Args:
            storage (Storage): Storage instance for loading and saving functions.
            name_filter (str): Pattern to match data names to load.
            param_types (List[ParamType]): Additional parameter types beyond the defaults.
            category (str): Optional category for all functions in this registry.
        """
        self.storage = storage
        self.name_filter = name_filter
        self.description = None
        self.functions = {}
        self.category = category
        
        # Combine default and custom param types
        all_param_types = list(self.DEFAULT_PARAM_TYPES)
        if param_types:
            all_param_types.extend(param_types)
        
        # Build type name to instance mapping
        self.param_types = {}
        for param_type in all_param_types:
            if param_type.name in self.param_types:
                raise ValueError(f"Duplicate parameter type name: {param_type.name}")
            self.param_types[param_type.name] = param_type
        
        self.load(name_filter, merge=True)


    def load(self, name_filter: str = None, merge: bool = False):
        """
        Load functions from the storage that match the specified data name pattern.

        Args:
            name_filter (str, optional): Pattern to match data names to load. Defaults to instance's name_filter.
            merge (bool, optional): Whether to merge with existing functions. Defaults to False.
        """         
        if not merge:
            self.clear()
            
        matched_data_names = fnmatch.filter(self.storage.list(), name_filter or self.name_filter)
        
        for name in matched_data_names:
            data = self.storage.load(name)
            self.description = data.get("description", "Missing description!")
            self._merge_functions(data["functions"])


    def clear(self):
        """
        Clear the existing functions.
        """
        self.functions = {}


    def _merge_functions(self, new_functions: Dict[str, Dict]):
        """
        Merge new functions into the registry.

        Args:
            new_functions (Dict[str, Dict]): Dictionary of new functions to add.

        Raises:
            KeyError: If a function key already exists in the registry.
        """
        for key, info in new_functions.items():
            
            if key in self.functions:
                raise KeyError(f"Function key '{key}' already exists in the registry.")
            
            try:
                self.functions[key] = FunctionInfo(info, self.param_types, self.category)
            except Exception as e:
                raise RuntimeError(f"Error processing function key '{key}': {str(e)}") from e

            
    def get_function_keys(self) -> List[str]:
        """
        Retrieve a list of all function names in the registry.

        Returns:
            List[str]: List of all function keys.
        """
        return list(self.functions.keys())


    def has_function(self, key: Hashable) -> bool:
        """
        Check if a function with a given name exists in the registry.

        Args:
            key (Hashable): The function key to check.

        Returns:
            bool: True if the function exists, False otherwise.
        """
        return key in self.functions


    def get_function_info(self, key: Hashable) -> FunctionInfo:
        """
        Retrieve the function info for a given function name.

        Args:
            key (Hashable): The function key to retrieve.

        Returns:
            FunctionInfo: The function information object.
        """
        return self.functions[key]


    def get_all_param_defaults(self) -> Dict[str, Dict[str, Any]]:
        """
        Retrieve default parameters for all functions in the registry.
        Returns: Dictionary mapping function names to parameter dictionaries.
        """
        return {
            key: {param.name: param.default for param in info.params}
            for key, info in self.functions.items()
        }
