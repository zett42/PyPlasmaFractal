import enum
from typing import List, Hashable, Dict

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

class FunctionRegistry:
    """
    A generic base class for storing and managing function entries.
    All entries are expected to be instances of FunctionInfo or its subtypes.
    """
    # Static dictionary to store all functions by name, to be defined by derived classes.
    functions: Dict[Hashable, FunctionInfo] = {}
    
    @classmethod
    def has_function(cls, key: Hashable) -> bool:
        """
        Check if a function with a given name exists in the registry.
        """
        return key in cls.functions
    
    @classmethod
    def get_function_info(cls, key: Hashable) -> FunctionInfo:
        """
        Retrieve the function info for a given function name.
        """
        return cls.functions[key]
    
    @classmethod
    def get_all_function_keys(cls) -> List[str]:
        """
        Retrieve a list of all function names in the registry.
        """
        return list(cls.functions.keys())

    @classmethod
    def max_param_count(cls) -> int:
        """
        Compute the maximum number of parameters among all functions in the registry.
        """
        return max(len(info.params) for info in cls.functions.values())

    @classmethod
    def get_all_param_defaults(cls, use_string_keys: bool = False) -> Dict[str, List[float]]:
        """
        Retrieve default parameters for all functions in the registry.
        This method converts enum keys to string representations if use_string_keys is True.
        Assumes each function conforms to having 'params' with 'default' attributes.
        """
        result = {}
        
        for key, info in cls.functions.items():
            
            # Optionally convert enum keys to string
            if use_string_keys and isinstance(key, enum.Enum):
                key = key.name
                
            result[key] = [param.default for param in info.params]

        return result
