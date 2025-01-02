from abc import ABC, abstractmethod
from typing import List, Hashable, Dict, Any, Set, Tuple, Union
import fnmatch
from PyPlasmaFractal.mylib.config.storage import Storage


class DynamicAttributes:
    """
    A class for managing dynamic attributes initialized from a dictionary.
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


class ParamType(ABC):
    """
    Abstract base class for parameter types used in functions.
    """
    
    @property
    @abstractmethod
    def type_name(self) -> str:
        """Return the type name for this parameter type."""
        pass

    @property
    @abstractmethod
    def mandatory_attributes(self) -> Set[str]:
        """Return the mandatory attributes for this parameter type."""
        pass

    @abstractmethod
    def create_default(self) -> Any:
        """Create a default value for this parameter type."""
        pass

    @abstractmethod
    def convert(self, value: Any, attributes: Dict[str, Any]) -> Any:
        """"""
        pass


class IntParamType(ParamType):
    """
    A class for handling integer parameter types.
    """
    
    @property
    def type_name(self) -> str:
        return "int"
 
    @property
    def mandatory_attributes(self) -> Set[str]:
        return {'min', 'max'}

    def create_default(self) -> int:
        return 0
               
    def convert(self, value: Any, attributes: Dict[str, Any]) -> int:
        try:
            converted = int(value)
        except (TypeError, ValueError):
            raise ValueError(f"Cannot convert {value} to integer")
            
        min_val = attributes['min']
        max_val = attributes['max']
        if not (min_val <= converted <= max_val):
            raise ValueError(f"Value {converted} outside range [{min_val}, {max_val}]")
        return converted


class FloatParamType(ParamType):
    """
    A class for handling float parameter types.
    """
    
    @property
    def type_name(self) -> str:
        return "float"
    
    @property
    def mandatory_attributes(self) -> Set[str]:
        return {'min', 'max'}
 
    def create_default(self) -> float:
        return 0.0
          
    def convert(self, value: Any, attributes: Dict[str, Any]) -> float:
        try:
            converted = float(value)
        except (TypeError, ValueError):
            raise ValueError(f"Cannot convert {value} to float")
            
        min_val = attributes['min']
        max_val = attributes['max']
        if not (min_val <= converted <= max_val):
            raise ValueError(f"Value {converted} outside range [{min_val}, {max_val}]")
        return converted


class ColorParamType(ParamType):
    """
    A class for handling color parameter types.
    """
    
    @property
    def type_name(self) -> str:
        return "color"
    
    @property
    def mandatory_attributes(self) -> Set[str]:
        return set()  # No mandatory attributes for RGBA colors
    
    
    def create_default(self) -> List[float]:
        return [0.0, 0.0, 0.0, 1.0]  # Black with full opacity
    

    def convert(self, value: Any, attributes: Dict[str, Any]) -> List[float]:
        
        if isinstance(value, str):  # Handle hex colors
            return self._from_hex(value)
        if isinstance(value, (list, tuple)):
            return self._normalize_components(value)
        raise ValueError(f"Cannot convert {value} to color")
    
    
    def _from_hex(self, hex_str: str) -> List[float]:
        
        # Remove # if present
        hex_str = hex_str.lstrip('#')
        if len(hex_str) not in (6, 8):  # RGB or RGBA
            raise ValueError("Invalid hex color")
        try:
            rgb = [int(hex_str[i:i+2], 16)/255.0 for i in (0, 2, 4)]
            alpha = int(hex_str[6:8], 16)/255.0 if len(hex_str) == 8 else 1.0
            return rgb + [alpha]
        except ValueError:
            raise ValueError("Invalid hex color format")
        
    
    def _normalize_components(self, components: Union[List, Tuple]) -> List[float]:
        
        if len(components) not in (3, 4):
            raise ValueError("Color must have 3 or 4 components")
        
        # Convert to float and normalize if needed
        normalized = []
        for v in components:
            if isinstance(v, (int, float)):
                if v > 1.0:  # Assume 0-255 range
                    v = v / 255.0
                normalized.append(float(v))
            else:
                raise ValueError(f"Invalid color component: {v}")
                
        # Add alpha if missing
        if len(normalized) == 3:
            normalized.append(1.0)
            
        if not all(0.0 <= v <= 1.0 for v in normalized):
            raise ValueError("Color components must be in range [0, 1]")
            
        return normalized


class FunctionParam(DynamicAttributes):
    """Information about a parameter used in (shader) functions and how to represent it in the UI."""
    
    def __init__(self, attributes: Dict[str, Any], param_types: Dict[str, ParamType]):
        """
        Initialize the FunctionParam instance.
        
        Args:
            attributes (Dict[str, Any]): Dictionary of attributes to set on the instance.
            param_types (Dict[str, ParamType]): Dictionary of parameter types to use.
        """

        # Convert param_type to ParamType instance        
        attributes['param_type'] = param_types.get(attributes.get('param_type', 'float'), FloatParamType())
        
        # Combine default mandatory attributes with param_type's mandatory attributes
        mandatory = ['name', 'display_name', 'param_type', 'default'] + list(attributes['param_type'].mandatory_attributes)

        # Call super to validate and set attributes                          
        super().__init__(attributes, mandatory_attrs=mandatory)
        
        # Convert default value and update attribute
        try:
            self.default = self.param_type.convert(self.default, attributes)
        except Exception as e:
            raise ValueError(f"Failed to convert default value for parameter '{self.name}': {str(e)}") from e


class FunctionInfo(DynamicAttributes):
    """Contains information about a function, including its parameters."""
    
    def __init__(self, attributes: Dict[str, Any], param_types: Dict[str, ParamType]):
        """
        Initialize the FunctionInfo instance.
        
        Args:
            attributes (Dict[str, Any]): Dictionary of attributes to set on the instance.
            param_types (Dict[str, ParamType]): Dictionary of parameter types to use.
        """
        
        # Convert params to FunctionParam instances
        attributes['params'] = [FunctionParam(param, param_types) for param in attributes['params']]
        
        super().__init__(attributes, mandatory_attrs=['display_name', 'params'])


class FunctionRegistry:
    """
    A class for storing and managing function information.
    """
    
    DEFAULT_PARAM_TYPES = [
        IntParamType(),
        FloatParamType(),
        ColorParamType()
    ]
    
    def __init__(self, storage: Storage, name_filter: str = "*", param_types: List[ParamType] = None):
        """
        Initialize the FunctionRegistry instance.

        Args:
            storage (Storage): Storage instance for loading and saving functions.
            name_filter (str): Pattern to match data names to load.
            param_types (List[ParamType]): Additional parameter types beyond the defaults.
        """
        self.storage = storage
        self.name_filter = name_filter
        self.description = None
        self.functions = {}
        
        # Combine default and custom param types
        all_param_types = list(self.DEFAULT_PARAM_TYPES)
        if param_types:
            all_param_types.extend(param_types)
        
        # Build type name to instance mapping
        self.param_types = {}
        for param_type in all_param_types:
            if param_type.type_name in self.param_types:
                raise ValueError(f"Duplicate parameter type name: {param_type.type_name}")
            self.param_types[param_type.type_name] = param_type
        
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
                self.functions[key] = FunctionInfo(info, self.param_types)
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
