"""
This module provides wrapper functions for ImGui controls to update attributes of objects or elements in lists more directly, with less code. 
"""

from enum import Enum
from pathlib import Path
import re
import imgui
from typing import *

from PyPlasmaFractal.mylib.gui.ansi_style import AnsiStyle
from PyPlasmaFractal.mylib.gui.trim_string import trim_path_with_ellipsis

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


def slider_int(label: str, obj: object, attr: str = None, index: Optional[int] = None, min_value: int = 0, max_value: int = 1, multiple: int = 1) -> bool:
    """
    Creates and manages an ImGui integer slider for modifying a property of an object or a specific index within a collection.
    Optionally rounds the slider value to the nearest multiple of a specified number.

    Args:
        label (str): The label for the slider in the ImGui interface.
        obj (object): The object or collection containing the property to update.
        attr (str, optional): The name of the attribute within the object to modify. If None, `obj` should be a collection, and `index` must be specified.
        index (int, optional): The index within the collection attribute to modify. Relevant when `attr` points to a collection or `obj` itself is a collection.
        min_value (int): The minimum value of the slider.
        max_value (int): The maximum value of the slider.
        multiple (int): The value to which the slider's output will be rounded. Default is 1, which means no rounding.

    Returns:
        True if the value has changed, False otherwise.
    """
    return _manage_attribute_interaction(
        obj,
        attr=attr,
        index=index,
        interaction_func=lambda display_value, _: imgui.slider_int(label, display_value, min_value, max_value),
        convert_to_display=lambda x: (x // multiple) * multiple if multiple > 1 else x,
        convert_from_display=lambda x, _: (x // multiple) * multiple if multiple > 1 else x
    )


def slider_float(label: str, obj: object, attr: str = None, index: Optional[IndexType] = None, min_value: float = 0.0, max_value: float = 1.0, flags: int = 0) -> bool:
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
        True if the value has changed, False otherwise.
    """
    return _manage_attribute_interaction(
        obj, 
        attr=attr,
        index=index,
        interaction_func=lambda display_value, current_value: imgui.slider_float(label, display_value, min_value, max_value, flags=flags)
    )


def checkbox(label: str, obj: object, attr: str = None, index: Optional[IndexType] = None) -> bool:
    """
    Creates and manages an ImGui checkbox for toggling a boolean attribute of an object directly or within a collection.

    Args:
        label (str): The label to display next to the checkbox.
        obj (object): The object or collection containing the attribute to update.
        attr (str, optional): The name of the attribute to update. If None, `obj` should be a collection, and `index` must be specified.
        index (int, optional): The index within a collection attribute to update, used when `attr` points to a collection.

    Returns:
        True if the value has changed, False otherwise.
    """
    return _manage_attribute_interaction(
        obj, 
        attr=attr, 
        index=index,
        interaction_func=lambda display_value, current_value: imgui.checkbox(label, display_value)
    )


def list_combo(label: str, obj: object, attr: str = None, index: int = None, items: list = [] ) -> bool:
    """
    Creates an ImGui combo box for selecting a value from a provided list, modifying an attribute of an object directly or at a specified index within a collection using a centralized attribute management function.

    Args:
        label (str): The label for the combo box.
        items (list): List of items to be displayed in the combo box.
        obj (object): The object containing the attribute to be updated.
        attr (str, optional): The attribute name to update. If None, `obj` should be a collection, and `index` must be specified.
        index (int, optional): The index within the collection attribute to update, applicable if `attr` points to a collection.

    Returns:
        True if the value has changed, False otherwise.
    """

    # Convert items to strings for display purposes
    display_items = [str(item) for item in items]

    def interaction(current_index, current_value):
        # Use display_items for imgui combo
        changed, new_index = imgui.combo(label, current_index, display_items)
        return changed, new_index

    def convert_to_display(current_value):
        # Use the index of the current value in items as the display value
        try:
            return items.index(current_value)
        except ValueError:
            return -1  # If current value is not in items

    def convert_from_display(index, _):
        # Convert the selected index back to the item from the original items list
        return items[index]

    return _manage_attribute_interaction(
        obj,
        interaction_func=interaction,
        attr=attr,
        index=index,
        convert_to_display=convert_to_display,
        convert_from_display=convert_from_display
    )


def enum_combo(label: str, obj: object, attr: str = None, index: Optional[IndexType] = None) -> bool:
    """
    Creates an ImGui combo box for selecting an enum value, modifying an attribute of an object directly or at a specified index within a collection.

    Args:
        label (str): The label for the combo box.
        obj (object): The object containing the attribute to be updated.
        attr (str, optional): The attribute name to update. If None, `obj` should be a collection, and `index` must be specified.
        index (int, optional): The index within the collection attribute to update, applicable if `attr` points to a collection.

    Returns:
        True if the value has changed, False otherwise.

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

    return _manage_attribute_interaction( 
        obj, 
        attr=attr, 
        index=index,
        interaction_func=interaction,
        convert_to_display=convert_to_display, 
        convert_from_display=convert_from_display
    )


def input_text(label: str, obj: object, attr: str = None, index: Optional[IndexType] = None, buffer_size: int = 256) -> bool:
    """
    Creates and manages an ImGui text input for modifying a string property of an object or a specific index within a collection.

    Args:
        label (str): The label for the text input in the ImGui interface.
        obj (object): The object or collection containing the property to update.
        attr (str, optional): The name of the attribute within the object to modify. If None, `obj` should be a collection, and `index` must be specified.
        index (IndexType, optional): The index within the collection attribute to modify. Relevant when `attr` points to a collection or `obj` itself is a collection.
        buffer_size (int): The maximum size of the input buffer, limiting the number of characters that can be entered.

    Returns:
        True if the value has changed, False otherwise.
    """
    return _manage_attribute_interaction(
        obj=obj,
        interaction_func=lambda display_value, _: imgui.input_text(label, display_value, buffer_size),
        attr=attr,
        index=index
    )


def input_int(label: str, obj: object, attr: str = None, index: Optional[IndexType] = None, step: int = 1, step_fast: int = 100) -> bool:
    """
    Creates and manages an ImGui integer input for modifying an integer property of an object or a specific index within a collection.

    Args:
        label (str): The label for the integer input in the ImGui interface.
        obj (object): The object or collection containing the property to update.
        attr (str, optional): The name of the attribute within the object to modify. If None, `obj` should be a collection, and `index` must be specified.
        index (IndexType, optional): The index within the collection attribute to modify. Relevant when `attr` points to a collection or `obj` itself is a collection.
        step (int): The step size for each increment or decrement of the value.
        step_fast (int): A larger step size for faster adjustments.

    Returns:
        True if the value has changed, False otherwise.
    """
    return _manage_attribute_interaction(
        obj=obj,
        interaction_func=lambda display_value, _: imgui.input_int(label, display_value, step, step_fast),
        attr=attr,
        index=index
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
        True if the value has changed, False otherwise.

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

            return True  # Return True to indicate a change
    
    return False  # Return False if no change occurred


class resized_items:
    """
    A context manager for temporarily resizing ImGui items.

    This class is used as a context manager to temporarily set the width of ImGui items.
    It pushes the specified width using `imgui.push_item_width()` when entering the context,
    and pops the width using `imgui.pop_item_width()` when exiting the context.

    Parameters:
    - width: The width to set for the ImGui items.
        0.0 - default to ~2/3 of windows width
        >0.0 - width in pixels
        <0.0 - align xx pixels to the right of window (so -FLOAT_MIN always align width to the right side)

    Usage:
    ```
    with resized_items(width):
        # Code that uses ImGui items with the specified width
    ```
    """

    def __init__(self, width):
        self.width = width

    def __enter__(self):
        imgui.push_item_width(self.width)
        return self.width
    
    def __exit__(self, exc_type, exc_value, traceback):
        imgui.pop_item_width()


def display_trimmed_path_with_tooltip(path: Union[Path, str], available_width: int, margin: int = 6, ellipsis: str = '...'):
    """
    Display a trimmed path with a tooltip showing the full path.

    Args:
        path (str): The path to be displayed.
        available_width (int): The available width for displaying the path.

    Returns:
        None
    """
    path = str(path)
    display_path = trim_path_with_ellipsis(path, available_width - margin, imgui_text_width, ellipsis)

    # Display the trimmed path and provide a tooltip with the full path
    imgui.text(display_path)      
    if imgui.is_item_hovered() and len(display_path) != len(path):
        imgui.set_tooltip(path)


def imgui_text_width(*args, **kwargs) -> int:
    """
    Calculates the width of the text rendered using the imgui library.

    Args:
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.

    Returns:
        int: The width of the rendered text.

    """
    return imgui.calc_text_size(*args, **kwargs)[0]


def show_tooltip(text: str):
    """
    Helper function to show a tooltip with basic Markdown rendering if the current item is hovered.
    It tries to display the tooltip in a fixed position to the right or left of the item, 
    aligned to the parent window's frame, based on the available space.
    
    Parameters:
        text (str): The text to display in the tooltip.
    """
    if imgui.is_item_hovered():
        _, item_min_y = imgui.get_item_rect_min()
        _, item_height = imgui.get_item_rect_size()
        
        window_pos_x, _ = imgui.get_window_position()
        window_size_x, _ = imgui.get_window_size()
        
        viewport = imgui.get_main_viewport()
        viewport_x, viewport_width = viewport.pos.x, viewport.size.x
        
        padding_x = imgui.get_style().window_padding.x
        
        # Calculate the correct text width
        tooltip_text_width = calculate_markdown_max_width(text) + 2 * padding_x
        
        tooltip_x = window_pos_x + window_size_x
        tooltip_y = item_min_y
        
        if tooltip_x + tooltip_text_width > viewport_x + viewport_width:
            tooltip_x = window_pos_x - tooltip_text_width
            if tooltip_x < viewport_x:
                tooltip_x = viewport_x
                tooltip_y += item_height
        
        imgui.set_next_window_position(tooltip_x, tooltip_y)
        imgui.set_next_window_size(tooltip_text_width, 0)
        imgui.begin_tooltip()
        
        render_markdown(text)
        
        imgui.end_tooltip()
        
        
def render_markdown(text: str):
    
    lines = text.split('\n')
    for line in lines:
        if line.startswith('# '):
            imgui.text_ansi(f"{AnsiStyle.FG_BRIGHT_RED}{line[2:]}{AnsiStyle.RESET}")
        elif line.startswith('## '):
            imgui.text_ansi(f"{AnsiStyle.FG_BRIGHT_BLUE}{line[3:]}{AnsiStyle.RESET}")
        elif line.startswith('- '):
            imgui.bullet()
            imgui.text_ansi(line[2:])
        elif line.startswith('**') and line.endswith('**'):
            imgui.text_ansi(f"{AnsiStyle.BOLD}{line[2:-2]}{AnsiStyle.RESET}")
        elif line.startswith('*') and line.endswith('*'):
            imgui.text_ansi(f"{AnsiStyle.UNDERLINE}{line[1:-1]}{AnsiStyle.RESET}")
        else:
            imgui.text_ansi(line)
            
            
def calculate_markdown_max_width(text: str):
    
    lines = text.split('\n')
    max_width = 0
    bullet_margin = imgui.get_style().indent_spacing
    for line in lines:
        stripped_line = strip_ansi_codes(line)
        if line.startswith('- '):
            line_width = imgui.calc_text_size(stripped_line).x + bullet_margin
        else:
            line_width = imgui.calc_text_size(stripped_line).x
        max_width = max(max_width, line_width)
    return max_width      
                    
        
ansi_escape = re.compile(r'\x1B[@-_][0-?]*[ -/]*[@-~]')

def strip_ansi_codes(text: str) -> str:
    """
    Strip ANSI escape codes from a string.
    """
    return ansi_escape.sub('', text)
