from typing import Any, Dict
from PyPlasmaFractal.mylib.config.json_merge import MergePolicy, handle_type_mismatch_gracefully, json_deep_merge

class SerializableConfig:
    """
    Base class for configuration objects that can be serialized to/from dictionaries.
    Provides common functionality for converting class attributes to dictionaries and
    merging dictionaries back into the object state.

    List Handling:
    All lists in configuration objects are expected to maintain their size during merging.
    When merging lists:
    - If source list is shorter: Only provided elements are updated, remaining elements keep their original values
    - If source list is longer: Extra elements are ignored
    This ensures data migration compatibility when list structures change between versions.
    """
    
    def __init__(self):
        """Initialize the SerializableConfig base class."""
        pass
        
    def to_dict(self) -> dict:
        """
        Convert the public attributes to a dictionary.
        Recursively converts nested SerializableConfig objects.

        Returns:
            dict: A dictionary representation of the instance.
        """
        result = {}
        for key, value in self.__dict__.items():
            if not key.startswith('_'):
                if isinstance(value, SerializableConfig):
                    result[key] = value.to_dict()
                else:
                    result[key] = value
        return result
             
    def merge_dict(self, source: dict) -> None:
        """
        Update the instance with the values from a dictionary.
        Only sets attributes from the dictionary that already exist in the instance.
        Handles type mismatches gracefully to avoid data migration issues.
        Preserves nested SerializableConfig objects by merging into them rather than replacing.

        Args:
            source (dict): Dictionary containing values to merge into this instance.
        """
        merged = json_deep_merge(
            self.to_dict(), 
            source, 
            default_merge_policy=MergePolicy.MERGE_EXISTING,
            handle_type_mismatch=handle_type_mismatch_gracefully
        )
        
        for key, value in merged.items():
            if key.startswith('_'):
                continue
                
            current_value = getattr(self, key, None)
            if isinstance(current_value, SerializableConfig) and isinstance(value, dict):
                # If we have a nested config object, merge into it instead of replacing it
                current_value.merge_dict(value)
            else:
                setattr(self, key, value)
