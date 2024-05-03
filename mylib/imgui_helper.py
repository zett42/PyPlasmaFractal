"""
This module provides wrapper functions for ImGui controls to update attributes of objects or elements in lists more directly, with less code. 
"""

from enum import Enum
import imgui
from typing import *

IndexType = Union[int, Hashable]

def collapsing_header(title: str, obj: Any, attr: str = None, index: Optional[IndexType] = None, flags: int = 0) -> bool:
    """
    Create and manage an ImGui collapsing header that updates a boolean attribute of an object or a specific index within a collection directly. It can use a default value if the attribute or index does not exist.

    Args:
        title (str): The title of the collapsing header in the ImGui interface.
        obj (Any): The object or collection containing the attribute to update.
        attr (str): The attribute name on the object corresponding to the boolean property.
        index (IndexType, optional): The index within the collection attribute to update.
        flags (int): Additional flags for the collapsing header.

    Returns:
        bool: The updated value of the boolean attribute.
    """
    current_state = [None]

    def interaction_func(display_value, _):
        open, _ = imgui.collapsing_header(title, flags=flags | (imgui.TREE_NODE_DEFAULT_OPEN if display_value else 0))
        current_state[0] = open
        return display_value != open, open

    _manage_attribute_interaction(
        obj=obj,
        interaction_func=interaction_func,
        attr=attr,
        index=index,
        convert_to_display=lambda x: x,
        default_value=True  # Default to open if the attribute does not exist
    )

    return current_state[0]


def slider_int(label: str, obj: object, attr: str = None, index: Optional[IndexType] = None, min_value: int = 0, max_value: int = 1) -> None:
    """
    Creates and manages an ImGui integer slider for modifying a property of an object or a specific index within a collection.

    Args:
        label (str): The label for the slider in the ImGui interface.
        obj (object): The object or collection containing the property to update.
        attr (str, optional): The name of the attribute within the object to modify. If None, `obj` should be a collection, and `index` must be specified.
        index (int, optional): The index within the collection attribute to modify. Relevant when `attr` points to a collection or `obj` itself is a collection.
        min_value (int): The minimum value of the slider.
        max_value (int): The maximum value of the slider.

    Returns:
        None: This function performs in-place modification and does not return a value.
    """
    _manage_attribute_interaction(
        obj, 
        attr=attr, 
        index=index,
        interaction_func=lambda display_value, current_value: imgui.slider_int(label, display_value, min_value, max_value)
    )


def slider_float(label: str, obj: object, attr: str = None, index: Optional[IndexType] = None, min_value: float = 0.0, max_value: float = 1.0, flags: int = 0) -> None:
    """
    Creates and manages an ImGui float slider for modifying a property of an object or a specific index within a collection.

    Args:
        label (str): The label text to display next to the slider.
        obj (object): The object or collection containing the property to be modified.
        attr (str, optional): The name of the attribute within the object to modify. If None, `obj` should be a collection, and `index` must be specified.
        index (int, optional): The index within the collection attribute to modify. Relevant when `attr` points to a collection or `obj` itself is a collection.
        min_value (float): The minimum value of the slider.
        max_value (float): The maximum value of the slider.
        flags (int, optional): ImGui-specific flags to customize the slider behavior.

    Returns:
        None: This function performs in-place modification and does not return a value.
    """
    _manage_attribute_interaction(
        obj, 
        attr=attr,
        index=index,
        interaction_func=lambda display_value, current_value: imgui.slider_float(label, display_value, min_value, max_value, flags=flags)
    )


def checkbox(label: str, obj: object, attr: str = None, index: Optional[IndexType] = None) -> None:
    """
    Creates and manages an ImGui checkbox for toggling a boolean attribute of an object directly or within a collection.

    Args:
        label (str): The label to display next to the checkbox.
        obj (object): The object or collection containing the attribute to update.
        attr (str, optional): The name of the attribute to update. If None, `obj` should be a collection, and `index` must be specified.
        index (int, optional): The index within a collection attribute to update, used when `attr` points to a collection.

    Returns:
        None: This function performs in-place modification and does not return a value.
    """
    _manage_attribute_interaction(
        obj, 
        attr=attr, 
        index=index,
        interaction_func=lambda display_value, current_value: imgui.checkbox(label, display_value)
    )


def list_combo(label: str, obj: object, attr: str = None, index: int = None, items: list = [] ) -> None:
    """
    Creates an ImGui combo box for selecting a value from a provided list, modifying an attribute of an object directly or at a specified index within a collection using a centralized attribute management function.

    Args:
        label (str): The label for the combo box.
        items (list): List of items to be displayed in the combo box.
        obj (object): The object containing the attribute to be updated.
        attr (str, optional): The attribute name to update. If None, `obj` should be a collection, and `index` must be specified.
        index (int, optional): The index within the collection attribute to update, applicable if `attr` points to a collection.

    Returns:
        None: This function performs in-place modification and does not return a value.
    """

    def interaction(current_index, current_value):
        changed, new_index = imgui.combo(label, current_index, items)
        return changed, new_index

    def convert_to_display(current_value):
        # Use the index of the current value in items as the display value
        try:
            return items.index(current_value)
        except ValueError:
            return -1  # If current value is not in items

    def convert_from_display(index, _):
        # Convert the selected index back to the item
        return items[index]

    _manage_attribute_interaction(
        obj,
        interaction_func=interaction,
        attr=attr,
        index=index,
        convert_to_display=convert_to_display,
        convert_from_display=convert_from_display
    )


def enum_combo(label: str, obj: object, attr: str = None, index: Optional[IndexType] = None) -> None:
    """
    Creates an ImGui combo box for selecting an enum value, modifying an attribute of an object directly or at a specified index within a collection.

    Args:
        label (str): The label for the combo box.
        obj (object): The object containing the attribute to be updated.
        attr (str, optional): The attribute name to update. If None, `obj` should be a collection, and `index` must be specified.
        index (int, optional): The index within the collection attribute to update, applicable if `attr` points to a collection.

    Returns:
        None: This function performs in-place modification and does not return a value.

    Note:
        The enum type is inferred from the current value of the attribute. This function is designed to be used with enum attributes.
    """
    def interaction(current_index, current_value):
        options = [e.name for e in type(current_value)]
        return imgui.combo(label, current_index, options)  # Return both change flag and new index

    def convert_to_display(current_value):
        if not isinstance(current_value, Enum):
            raise TypeError(f"Expected an Enum type for attribute '{attr}', got {type(current_value).__name__} instead.")
        return [e.name for e in type(current_value)].index(current_value.name)

    def convert_from_display(index, current_value):
        enum_type = type(current_value)
        options = [e.name for e in enum_type]
        return enum_type[options[index]]

    _manage_attribute_interaction( 
        obj, 
        attr=attr, 
        index=index,
        interaction_func=interaction,
        convert_to_display=convert_to_display, 
        convert_from_display=convert_from_display
    )


def _manage_attribute_interaction(obj: Any, 
                                  interaction_func: Callable[[Any, Any], Tuple[bool, Any]], 
                                  attr: Optional[str] = None, 
                                  index: Optional[IndexType] = None,
                                  convert_to_display: Optional[Callable[[Any], Any]] = None, 
                                  convert_from_display: Optional[Callable[[int, Any], Any]] = None,
                                  default_value: Any = None
                                  ) -> None:
    """
    Manages the updating of an object's attribute or a specific element based on user interactions.

    Args:
        obj (Any): The target object or collection.
        interaction_func (Callable[[Any, Any], Tuple[bool, Any]]): Function that updates and returns change status.
        attr (Optional[str], optional): Attribute name of the object to interact with. If None, 'obj' is treated 
            directly or as a subscriptable entity if 'index' is specified.
        index (Optional[IndexType], optional): Index within 'obj' or its attribute if it's a collection, used to 
            specify which element to interact with. Defaults to None for direct interaction.
        convert_to_display (Optional[Callable[[Any], Any]], optional): Function to convert the value for display.
        convert_from_display (Optional[Callable[[int, Any], Any]], optional): Function to revert the display value 
            back to the original format.

    Raises:
        ValueError: If both 'attr' and 'index' are not provided, or 'attr' is empty.
        TypeError: If indexing is attempted on a non-subscriptable object.

    Returns:
        None: Updates are performed in-place; nothing is returned.

    Details:
        This function facilitates dynamic interaction by updating an object's attribute or directly modifying an 
        indexed element within the object. It is particularly useful for interacting with attributes that are 
        collections or the object itself when it is a collection.
    """
    
    # Validate input combinations
    if not attr and index is None:
        raise ValueError("Either 'attr' or 'index' must be provided.")
    
    if attr == '':
        raise ValueError("Attribute name cannot be an empty string.")

    if attr is None:
        target = obj
    else:
        target = getattr(obj, attr, default_value)

    if index is not None:
        if hasattr(target, 'get'):
            current_value = target.get(index, default_value)
        elif hasattr(target, '__getitem__'):
            try:
                current_value = target[index]
            except (IndexError, KeyError):
                current_value = default_value
        else:
            raise TypeError("Indexing is attempted on a non-subscriptable object.")
    else:
        current_value = target

    # Use conversion function if provided to prepare the display value
    display_value = convert_to_display(current_value) if convert_to_display else current_value

    # Execute the interaction function and get both change flag and new display value
    changed, new_display_value = interaction_func(display_value, current_value)

    # If changed, convert back and update the target
    if changed:
        new_value = convert_from_display(new_display_value, current_value) if convert_from_display else new_display_value
        if new_value != current_value:
            if index is not None:
                target[index] = new_value
            else:
                assert attr, "Attribute name must be non-empty when no index is provided."
                setattr(obj, attr, new_value)
