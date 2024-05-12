from enum import Enum, auto
import numbers
from typing import *

class MergePolicy(Enum):
    MERGE_EXISTING = auto()    
    MERGE_EXTEND = auto()
    OVERWRITE = auto()

def type_safe_json_merge(target: Any, 
                         source: Any, 
                         merge_policies: Dict[str, MergePolicy] = {},
                         default_merge_policy: MergePolicy = MergePolicy.MERGE_EXISTING,
                         convert_scalar: Callable[[Any, Any], Any] = None,
                         path: str = '') -> Any:
    """
    Recursively merges two JSON-like structures (`target` and `source`) according to specified merge policies.

    Merge policies dictate how merging behaves at different points in the structure:
    - MERGE_EXISTING: Default policy; merges source into target only for existing keys/indices.
    - MERGE_EXTEND: Extends target with source; adds new elements or keys from source not present in target.
    - OVERWRITE: Completely replaces the value at the target with the value from the source.

    Args:
    - target (Any): The target structure to be merged into.
    - source (Any): The source structure from which data is merged.
    - merge_policies (Dict[str, MergePolicy], optional): A dictionary mapping paths to specific merge policies.
      Paths are dot-separated strings representing nested structures, with square brackets for list indices,
      e.g., 'user.address.city' or 'users[0].name'.
    - default_merge_policy (MergePolicy, optional): The default merging behavior when no specific policy is provided.
    - convert_scalar (Callable[[Any, Any], Any], optional): A function to handle scalar value conversions between different types.
    - path (str, optional): The current path used for merging, accumulates during recursive calls to reflect deeper levels of the structure.

    Returns:
    - Any: The merged result as per the merge policies.
    """
       
    policy = merge_policies.get(path, default_merge_policy)

    # Directly overwrite the target with source if specified, making sure root is never overwritten
    if path and policy == MergePolicy.OVERWRITE:
        return source

    if isinstance(target, dict) and isinstance(source, dict):
        for key in source:
            new_path = f"{path}.{key}" if path else key
            if policy == MergePolicy.MERGE_EXTEND or key in target:
                # If the key is not in the target, it will be added, otherwise it will be merged
                target[key] = type_safe_json_merge(target.get(key, {}), source[key], merge_policies, default_merge_policy, convert_scalar, new_path)
                
        return target

    elif isinstance(target, list) and isinstance(source, list):
        if policy == MergePolicy.MERGE_EXTEND:
            # Extend the target list with the source list
            target.extend(source[len(target):])  

        # Merge up to the minimum length of the two lists
        for i in range(min(len(target), len(source))):
            new_path = f"{path}[{i}]"
            target[i] = type_safe_json_merge(target[i], source[i], merge_policies, default_merge_policy, convert_scalar, new_path)
            
        return target

    # Assume scalars if not dictionaries or lists

    # If types are the same, directly use source
    if type(target) == type(source):
        return source
    
    # If no conversion function is provided, return source to keep the type integrity
    if convert_scalar is None:
        return source
    
    return convert_scalar(source, target)


def convert_json_scalar(source: Any, target: Any) -> Any:
    """
    Safely converts scalar values between different data types for JSON-like data handling.

    This function is designed to handle type conversions gracefully, avoiding exceptions during data migrations. 
    It supports conversions between enums, strings, booleans, and numbers, reflecting common JSON data types and Python structures. 
    If a conversion is not feasible or fails, the function returns the target value unchanged, preserving the existing data structure.

    Supported conversions include:
    - Enum to string and string to Enum, based on Enum member names.
    - String to boolean ("true", "false") and vice versa.
    - Numeric values and their string representations.
    - Boolean to string conversion.

    Parameters:
    - source (Any): The value to be converted.
    - target (Any): The target value whose type indicates the desired conversion.

    Returns:
    - Any: The converted value if conversion is possible and successful; otherwise, returns the target unchanged.

    Examples:
    - convert_json_scalar("OPEN", StatusEnum) -> might return StatusEnum.OPEN if "OPEN" is a valid Enum member.
    - convert_json_scalar(StatusEnum.CLOSED, str) -> returns "CLOSED".
    - convert_json_scalar("true", bool) -> returns True.
    - convert_json_scalar("100", int) -> returns 100.
    - convert_json_scalar(200, str) -> returns "200".
    """
    try:
        if isinstance(target, Enum):
            if isinstance(source, str):
                # Try to convert string to Enum, if the string is a valid Enum name
                return type(target)[source]
            return target  # Return target if conversion is not applicable

        elif isinstance(source, Enum):
            if isinstance(target, str):
                # Convert Enum to string using the Enum's name
                return source.name

        elif isinstance(target, bool) and isinstance(source, str):
            # Safely convert string to boolean
            lower_source = source.strip().lower()
            if lower_source == "true":
                return True
            elif lower_source == "false":
                return False
            return target  # Return target if string is not a boolean value

        elif isinstance(target, numbers.Number) and isinstance(source, str):
            # Convert string to a number if possible
            return type(target)(source)
        elif isinstance(target, str) and isinstance(source, numbers.Number):
            # Convert number to string
            return str(source)

        elif isinstance(target, str) and isinstance(source, bool):
            # Convert boolean to string explicitly
            return str(source)

    except (ValueError, KeyError, TypeError):
        # Handle any exception silently and return the target
        return target

    return target  # Return target if no conversion rules apply or if exceptions were caught
