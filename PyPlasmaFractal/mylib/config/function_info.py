from abc import ABC, abstractmethod
from typing import List, Dict, Any, Set, Tuple, Union, TypeVar, Generic

T = TypeVar('T')


class DynamicAttributes:
    """
    A class for managing dynamic attributes initialized from a dictionary.
    """
    def __init__(self, attributes: Dict[str, Any], mandatory_attrs: List[str]):
        """
        Initialize the instance with given attributes from a dictionary.

        Args:
            attributes (Dict[str, Any]): Dictionary of attributes to set on the instance.
            mandatory_attrs (List[str]): List of attribute names that are mandatory.

        Raises:
            KeyError: If any mandatory attribute is missing from attributes.
        """
        for attr in mandatory_attrs:
            if attr not in attributes:
                raise KeyError(f"Mandatory attribute '{attr}' is missing.")
        
        for key, value in attributes.items():
            setattr(self, key, value)


class ParamType(ABC):
    """
    Abstract base class for parameter types used in functions.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Return the type name for this parameter type."""
        pass

    @abstractmethod
    def create_instance(self) -> Any:
        """Create a new instance of this parameter type."""
        pass

    @abstractmethod
    def convert(self, value: Any, constraints: Dict[str, Any]) -> Any:
        """
        Convert a value to this parameter type.
        
        Args:
            value (Any): The value to convert.
            constraints (Dict[str, Any]): Constrains to check during conversion.
        """
        pass


class StructuredParamType(ParamType):
    """Base class for structured parameter types that can be created from dictionaries."""
    
    @abstractmethod
    def describe_attributes(self) -> Dict[str, ParamType]:
        """Describe the child attributes of this parameter type."""
        pass

    def convert(self, value: Any, constraints: Dict[str, Any]) -> Any:
        """Convert a value to this parameter type using dictionary-based conversion."""

        instance = self.create_instance()
        
        if isinstance(value, instance.__class__):
            return value
        
        if isinstance(value, dict):
            # Set only attributes that exist in the instance
            for key, val in value.items():
                if hasattr(instance, key):
                    setattr(instance, key, val)
            return instance
            
        raise ValueError(f"Cannot convert {value} to {self.name}")


class IntParamType(ParamType):
    """
    A class for handling integer parameter types.
    """
    
    @property
    def name(self) -> str:
        return "int"
 
    def create_instance(self) -> int:
        return 0
               
    def convert(self, value: Any, constraints: Dict[str, Any]) -> int:
        try:
            converted = int(value)
        except (TypeError, ValueError):
            raise ValueError(f"Cannot convert {value} to integer")
            
        min_val = constraints['min']
        max_val = constraints['max']
        if not (min_val <= converted <= max_val):
            raise ValueError(f"Value {converted} outside range [{min_val}, {max_val}]")
        return converted
    

class FloatParamType(ParamType):
    """
    A class for handling float parameter types.
    """
    
    @property
    def name(self) -> str:
        return "float"
    
    def create_instance(self) -> float:
        return 0.0
          
    def convert(self, value: Any, constraints: Dict[str, Any]) -> float:
        try:
            converted = float(value)
        except (TypeError, ValueError):
            raise ValueError(f"Cannot convert {value} to float")
            
        min_val = constraints['min']
        max_val = constraints['max']
        if not (min_val <= converted <= max_val):
            raise ValueError(f"Value {converted} outside range [{min_val}, {max_val}]")
        return converted


class ColorParamType(ParamType):
    """
    A class for handling color parameter types.
    """
    
    @property
    def name(self) -> str:
        return "color"
    
      
    def create_instance(self) -> List[float]:
        return [0.0, 0.0, 0.0, 1.0]  # Black with full opacity
    

    def convert(self, value: Any, constraints: Dict[str, Any]) -> List[float]:
        
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


class DynamicEnumType(ParamType, Generic[T]):
    """
    A class for handling dynamic enum parameter types.
    """
    
    def __init__(self, allowed_values: Set[T], default: T = None):
        self.allowed_values = set(allowed_values)
        self.default = default or (next(iter(allowed_values)) if allowed_values else None)
    
    @property
    def name(self) -> str:
        return "dynamic_enum"
    
    def create_instance(self) -> T:
        return self.default
    
    def convert(self, value: Any, attributes: Dict[str, Any]) -> T:
        if value not in self.allowed_values:
            raise ValueError(f"Value {value} is not a valid value (allowed: {self.allowed_values})")
        return value
    

class FunctionParam(DynamicAttributes):
    """Information about a parameter used in (shader) functions and how to represent it in the UI."""
    
    def __init__(self, attributes: Dict[str, Any], param_types: Dict[str, ParamType]):
        """
        Initialize the FunctionParam instance.
        
        Args:
            attributes (Dict[str, Any]): Dictionary of attributes to set on the instance.
            param_types (Dict[str, ParamType]): Dictionary of parameter types to use.
        """
       
        # Call super to validate and set attributes                          
        super().__init__(attributes, mandatory_attrs=['name', 'display_name', 'param_type', 'default'])

        # Convert param_type to ParamType instance 
        self.param_type = param_types.get(self.param_type, FloatParamType())
        
        # Convert default value
        try:
            self.default = self.param_type.convert(self.default, attributes)
        except Exception as e:
            raise ValueError(f"Failed to convert default value for parameter '{self.name}': {str(e)}") from e


class ParamGroup:
    """Represents a group of related parameters."""
    
    def __init__(self, display_name: str):
        self.display_name = display_name
        self.params = []  # Will be populated with FunctionParam instances


class FunctionInfo(DynamicAttributes):
    """Contains information about a function, including its parameters."""
    
    def __init__(self, attributes: Dict[str, Any], param_types: Dict[str, ParamType]):
        """
        Initialize the FunctionInfo instance.
        
        Args:
            attributes (Dict[str, Any]): Dictionary of attributes to set on the instance.
            param_types (Dict[str, ParamType]): Dictionary of parameter types to use.
        """
               
        super().__init__(attributes, mandatory_attrs=['display_name', 'params'])

        # Convert params to FunctionParam instances
        self.params = [FunctionParam(param, param_types) for param in self.params]
        
        # Create parameter groups if defined
        self.param_groups = []
        param_name_to_param = {p.name: p for p in self.params}
        grouped_params = set()
        
        # Create groups from param_groups array if it exists
        if 'param_groups' in attributes:
            for group_info in attributes['param_groups']:
                group = ParamGroup(group_info['display_name'])
                group.params = [param_name_to_param[name] for name in group_info['params']]
                grouped_params.update(group_info['params'])
                self.param_groups.append(group)
        
        # Create "Parameters" group for ungrouped parameters
        ungrouped_params = [p for p in self.params if p.name not in grouped_params]
        if ungrouped_params or not self.param_groups:  # Add Parameters group if there are ungrouped params or no groups at all
            group = ParamGroup("Parameters")
            group.params = ungrouped_params
            self.param_groups.append(group)
