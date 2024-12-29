from enum import Enum
from typing import List, Hashable, Dict, Any
import fnmatch
from PyPlasmaFractal.mylib.config.storage import Storage


class DynamicAttributes:
    """
    Base class for handling objects with mandatory and optional attributes.
    """
    def __init__(self, attributes: Dict[str, Any], mandatory_attrs: List[str]):
        """
        Initialize the instance with given attributes.

        Args:
            attributes (Dict[str, Any]): Dictionary of attributes to set on the instance.
            mandatory_attrs (List[str]): List of attribute names that are mandatory.

        Raises:
            KeyError: If any mandatory attribute is missing from attributes.
        """
        for attr in mandatory_attrs:
            if attr not in attributes:
                raise KeyError(f"Mandatory attribute '{attr}' is required.")
            
        for key, value in attributes.items():
            setattr(self, key, value)


class ParamType(Enum):
    FLOAT = "float"
    COLOR = "color"


class FunctionParam(DynamicAttributes):
    """Information about a parameter used in functions and how to represent it in the UI."""
    
    def _validate_float(self, value) -> None:
        
        if not isinstance(value, (int, float)):
            raise ValueError("Float parameter requires numeric default")

    def _validate_color(self, value) -> None:
        
        if not (isinstance(value, list) and len(value) == 4):
            raise ValueError("Color parameter requires RGBA default [r,g,b,a]")

    def __init__(self, attributes: Dict[str, Any]):
        
        if 'param_type' not in attributes:
            attributes['param_type'] = ParamType.FLOAT
        else:
            attributes['param_type'] = ParamType(attributes['param_type'])
            
        match attributes['param_type']:
            case ParamType.FLOAT:
                mandatory = ['display_name', 'min', 'max', 'default']
                self._validate_float(attributes.get('default'))
            case ParamType.COLOR:
                mandatory = ['display_name', 'default']
                self._validate_color(attributes.get('default'))
            case _:
                raise ValueError(f"Unsupported parameter type: {attributes['param_type']}")
                
        super().__init__(attributes, mandatory_attrs=mandatory)
        

class FunctionInfo(DynamicAttributes):
    """
    Contains information about a function, including its parameters.
    """
    def __init__(self, attributes: Dict[str, Any]):
        """
        Initialize a FunctionInfo instance.

        Args:
            attributes (Dict[str, Any]): Dictionary of attributes for the function.

        Raises:
            KeyError: If any mandatory attribute is missing from attributes.
        """
        # Make sure params are converted to FunctionParam instances (instead of just dictionaries)      
        attributes['params'] = [FunctionParam(param) for param in attributes['params']]
        
        super().__init__(attributes, mandatory_attrs = ['display_name', 'description', 'params'])


class FunctionRegistry:
    """
    A class for storing and managing function information.
    """
    def __init__(self, storage: Storage, name_filter: str = "*"):
        """
        Initialize the FunctionRegistry instance.

        Args:
            storage (Storage): Storage instance for loading and saving functions.
            name_filter (str): Pattern to match data names to load.
        """
        self.storage = storage
        self.name_filter = name_filter
        self.description = None
        self.functions = {}
        
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
            self.functions[key] = FunctionInfo(info)

            
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


    def get_function_display_name(self, key: Hashable) -> str:
        """
        Retrieve the function display name for a given function name.
        """
        return self.functions[key].display_name
    
    
    def get_function_params(self, key: Hashable) -> List[FunctionParam]:
        """
        Retrieve the function parameters for a given function name.
        """
        return self.functions[key].params


    def max_param_count(self) -> int:
        """
        Compute the maximum number of parameters among all functions in the registry.

        Returns:
            int: The maximum number of parameters.
        """
        return max(len(info.params) for info in self.functions.values())


    def get_all_param_defaults(self) -> Dict[str, List[float]]:
        """
        Retrieve default parameters for all functions in the registry.

        Returns:
            Dict[str, List[float]]: Dictionary mapping function keys to a list of default parameter values.
        """
        return {
            key: [param.default for param in info.params] 
            for key, info in self.functions.items()
        }
