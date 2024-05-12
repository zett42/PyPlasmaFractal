from enum import Enum, auto
import logging
import numbers
from typing import *

logger = logging.getLogger(__name__)
    
class MergePolicy(Enum):
    MERGE_EXTEND = auto()
    MERGE_EXISTING = auto()    
    OVERWRITE = auto()

def json_deep_merge(target: Any, 
                    source: Any, 
                    merge_policies: Dict[str, MergePolicy] = None,
                    default_merge_policy: MergePolicy = MergePolicy.MERGE_EXTEND,
                    handle_type_mismatch: Callable[[Any, Any], Any] = None,
                    path: str = '') -> Any:
    """
    Recursively merges two JSON-like structures (`target` and `source`) based on defined merging policies and 
    optional type mismatch handling. The function supports deep merging of nested dictionaries and lists, and 
    applies different merging strategies based on the merge policy defined for specific paths within the structures.

    Overview of Merge Policies:
    - MERGE_EXTEND: Merges elements from `source` into `target`. For lists, elements in `source` are appended to 
                    `target` after existing elements, unless the indices already exist, in which case the element
                    at that index in `target` is updated.
    - MERGE_EXISTING: Updates values in `target` with values from `source` only for existing keys or indices. No 
                    new keys or indices are added to `target`.
    - OVERWRITE: Replaces the existing element in `target` with the element from `source` at the same path, 
                except at the root level, where the `OVERWRITE` policy does not replace the entire `target` but 
                instead updates it in place to avoid potential errors.

    Type mismatches are handled via an optional callback, which can either convert incompatible types or raise an 
    exception to ensure data integrity. This callback is especially useful in complex data structures where type 
    consistency must be maintained.

    Args:
        target (Any): The base structure into which the `source` structure is merged. This root structure is not 
                    replaced when the `OVERWRITE` policy is used, preserving the top-level container.
        source (Any): The structure that provides new values to be merged into the `target`.
        merge_policies (Dict[str, MergePolicy], optional): A dictionary where keys represent nested paths in the 
            structures with specific merging policies as values. Supports dot and bracket notation for paths.
        default_merge_policy (MergePolicy, optional): The default merge policy to apply when no specific policy 
            is provided for a path.
        handle_type_mismatch (Callable[[Any, Any], Any], optional): A function that is called when a type mismatch 
            occurs during merging. This function should either resolve the mismatch or raise an exception.
        path (str, optional): Used internally to track the current path during recursion. Initially empty.

    Returns:
        Any: The resulting structure after merging `source` into `target` according to the specified policies and 
        type mismatch handling.

    Raises:
        TypeError: If a type mismatch occurs and `handle_type_mismatch` is not provided or if it fails to resolve 
            the mismatch without raising an exception.
        ValueError: If an invalid merge policy is encountered.
    """
    
    merge_policies = merge_policies or {}
    
    policy = merge_policies.get(path, default_merge_policy)
    if not isinstance(policy, MergePolicy):
        raise ValueError(f"Invalid merge policy: {policy}") 

    # Directly overwrite the target with source if specified, making sure root is never overwritten
    if path and policy == MergePolicy.OVERWRITE:
        return source

    if isinstance(target, dict) and isinstance(source, dict):
        for key in source:
            new_path = f"{path}.{key}" if path else key
            
            if key in target:
                target[key] = json_deep_merge(target[key], source[key], merge_policies, default_merge_policy, handle_type_mismatch, new_path)
            elif policy == MergePolicy.MERGE_EXTEND:
                target[key] = source[key]
                        
        return target

    elif isinstance(target, list) and isinstance(source, list):
        if policy == MergePolicy.MERGE_EXTEND:
            # Extend the target list with the source list
            target.extend(source[len(target):])  

        # Merge up to the minimum length of the two lists
        for i in range(min(len(target), len(source))):
            new_path = f"{path}[{i}]"
            target[i] = json_deep_merge(target[i], source[i], merge_policies, default_merge_policy, handle_type_mismatch, new_path)
            
        return target

    # At this point, target and source are either incompatible types or scalar values.

    if type(target) == type(source):
        # Types are the same, so assume they are scalar values and return the source
        return source
    
    # Use the type mismatch handler if supplied
    if handle_type_mismatch:
        try:
            return handle_type_mismatch(path, target, source)
        except Exception as e:
            error_msg = f"JSON type mismatch cannot be handled at '{path}': {type(target).__name__} vs {type(source).__name__}"
            logger.error(error_msg)
            raise TypeError(f"{error_msg}: {e}") from e
   
    error_msg = f"Unhandled JSON type mismatch at '{path}': {type(target).__name__} vs {type(source).__name__}"
    logger.error(error_msg)
    raise TypeError(error_msg)


def handle_type_mismatch_gracefully(path: str, target: Any, source: Any) -> Any:
    """
    Provides a lenient approach to handling type mismatches during JSON merging. Attempts to convert `source` to 
    the type of `target` or vice versa, and falls back to the original `target` if conversion is not feasible.

    This function is designed to be used as the `handle_type_mismatch` parameter in `json_deep_merge`. It supports
    conversions between common scalar types (e.g., strings to numbers, enums to strings) and handles cases where
    `target` or `source` may be an enumeration.

    Args:
        target (Any): The value that `source` should potentially be converted to match in type.
        source (Any): The value to be converted to the type of `target`.

    Returns:
        Any: The converted value if possible, otherwise returns `target` as a safe fallback.

    Note:
        This function ignores conversion errors internally and will default to returning `target` whenever a 
        conversion attempt fails. This ensures that the operation does not raise exceptions but also means that 
        in some cases, mismatches may be silently bypassed.
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

    except Exception as e:
        error_msg = f"JSON type mismatch cannot be handled at '{path}': {type(target).__name__} vs {type(source).__name__}"
        logger.warning(f"{error_msg}: {e}")
        pass  # Ignore conversion errors

    return target  # Safe fallback to the target value if conversion is not possible
