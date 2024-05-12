from typing import *

class FunctionParam:
    """
    Information about a parameter used in functions and how to represent it in the UI.
    """
    def __init__(self, display_name: str, min=0.0, max=1.0, logarithmic: bool=False, default=0.0):
        
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
    A generic base class for storing and managing function entries (e.g., warp functions, blend modes).
    All entries are expected to be instances of FunctionInfo or its subtypes, ensuring a consistent structure.
    """
    # Static dictionary to store all functions by name, to be defined by derived classes.
    functions = {}
    
    @classmethod
    def get_function_info(cls, function_name: str) -> FunctionInfo:
        """
        Retrieve the function info for a given function name.
        """
        function_info = cls.functions.get(function_name, None)
        if function_info:
            return function_info
        else:
            raise ValueError(f"No function info found for function name: {function_name}")
    
    @classmethod
    def get_all_function_names(cls) -> List[str]:
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
    def get_all_param_defaults(cls) -> dict[str, List[float]]:
        """
        Retrieve default parameters for all functions in the registry.
        This assumes each function conforms to having 'params' with 'default' attributes.
        """
        return {
            name: [param.default for param in info.params]
            for name, info in cls.functions.items()
        }
