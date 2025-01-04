import imgui
import math
from typing import Any, Dict
from pathlib import Path
import platform
import os
import logging

from PyPlasmaFractal.mylib.config.function_info import FunctionParam
from PyPlasmaFractal.mylib.config.function_registry import FunctionRegistry
from PyPlasmaFractal.mylib.gui.ansi_style import AnsiStyle
from PyPlasmaFractal.mylib.gui.icons import Icons
import PyPlasmaFractal.mylib.gui.imgui_helper as ih
from PyPlasmaFractal.plasma_fractal_params import PlasmaFractalParams


def noise_controls(noise_params: Any, unique_id: str, noise_registry: FunctionRegistry):
    """
    Creates the GUI controls for noise parameters.

    Args:
        noise_params: The noise parameters object to modify
        unique_id: Used to create unique control IDs
        noise_registry: The registry containing noise functions
    """
    function_combo(f"Noise Algorithm##{unique_id}", noise_params, 'noise_algorithm', noise_registry)

    ih.slider_float("Speed##{unique_id}", noise_params, 'speed', min_value=0.01, max_value=10.0)
    ih.show_tooltip("Adjust the speed of the noise.\n"
                   "Higher values result in faster movement of the noise pattern.")
    
    ih.slider_float("Scale##{unique_id}", noise_params, 'scale', min_value=0.01, max_value=100.0, flags=imgui.SLIDER_FLAGS_LOGARITHMIC)
    ih.show_tooltip("Adjust the scale of the noise.")
  
    ih.slider_int("Num. Octaves##{unique_id}", noise_params, 'octaves', min_value=1, max_value=12)
    ih.show_tooltip("Set the number of noise octaves for fractal generation.\n"
                     "Higher values increase detail but can be computationally intensive.")
    
    ih.slider_float("Gain/Octave##{unique_id}", noise_params, 'gain', min_value=0.1, max_value=1.0)
    ih.show_tooltip("Adjust the gain applied to the noise value produced by each octave.\n"
                     "A typical value is 0.5, which reduces the influence of higher octaves.")
    
    ih.slider_float("Pos. Scale/Octave##{unique_id}", noise_params, 'position_scale_factor', min_value=0.1, max_value=10.0)
    ih.show_tooltip("Adjust the position scale applied to each octave.\n"
                     "A typical value is 2.0, which allows each octave to contribute smaller details.")
    
    ih.slider_float("Rotation/Octave##{unique_id}", noise_params, 'rotation_angle_increment', min_value=0.0, max_value=math.pi * 2, flags=imgui.SLIDER_FLAGS_LOGARITHMIC)
    ih.show_tooltip("Adjust the rotation angle increment applied to each octave.")
    
    ih.slider_float("Time Scale/Octave##{unique_id}", noise_params, 'time_scale_factor', min_value=0.1, max_value=2.0)
    ih.show_tooltip("Adjust the time scale factor applied to each octave.\n"
                     "Higher values speed up the temporal changes of each octave.")
    
    ih.slider_float("Time Offset/Octave##{unique_id}", noise_params, 'time_offset_increment', min_value=0.0, max_value=20.0)
    ih.show_tooltip("Adjust the time offset increment applied to each octave,\n"
                     "to increase noise variation.")


def function_combo(combo_label: str, params: Any, params_attr: str, registry: FunctionRegistry):
    """
    Displays a combo box for selecting a function from the registry by display name,
    and updates the specified parameter in params with the selected function key.

    Args:
        combo_label (str): The label to display for the combo box.
        params (object): The object to update with the selected function key.
        params_attr (str): The attribute of the params object to update.
        registry (FunctionRegistry): The function registry containing the functions.
    """
    # Retrieve all function keys and their display names
    function_keys = registry.get_function_keys()
    function_display_names = [registry.get_function_info(key).display_name for key in function_keys]

    # Create a sorted list of (display_name, key) tuples
    sorted_functions = sorted(zip(function_display_names, function_keys))
    sorted_display_names, sorted_keys = zip(*sorted_functions)

    # Convert the tuples to lists
    sorted_display_names = list(sorted_display_names)
    sorted_keys = list(sorted_keys)

    # Find the current index based on the function key stored in params
    current_key = getattr(params, params_attr)
    current_index = sorted_keys.index(current_key) if current_key in sorted_keys else 0

    # Display the combo box with display names and update the selected key in params
    changed, selected_index = imgui.combo(f"{combo_label}##{params_attr}", current_index, sorted_display_names)

    if changed:
        setattr(params, params_attr, sorted_keys[selected_index])
        
    # Show a tooltip with details of all available functions in sorted order
    tooltip_text = f"# {registry.description}\n"
    for key in sorted_keys:
        color = AnsiStyle.FG_BRIGHT_YELLOW if key == current_key else AnsiStyle.FG_BRIGHT_CYAN
        func_info = registry.get_function_info(key)
        tooltip_text += f"\n- {color}{func_info.display_name}{AnsiStyle.RESET} - {func_info.description}"

    ih.show_tooltip(tooltip_text)
    

def function_settings(ui_state: object, 
                      header: str, 
                      header_attr: str, 
                      registry: FunctionRegistry,
                      function_attr: str,
                      params_attr: str,
                      params: PlasmaFractalParams):
    """
    Display the setting controls for a specific function.
    
    Args:
        ui_state: The object containing the UI state attributes.
        header: The header text to display.
        header_attr: The attribute name for the header state.
        registry: The function registry containing the function information.
        function_attr: The attribute name for the selected function key.
        params_attr: The attribute name for the function parameters dictionary.
        params: The PlasmaFractalParams object to update.    
    """
    
    if ih.collapsing_header(header, ui_state, attr=header_attr):
        
        # Dropdown for the available functions 
        function_combo(f"Function##{function_attr}", params, function_attr, registry)        
                    
        selected_function = getattr(params, function_attr)
        function_info = registry.get_function_info(selected_function)
        function_params_dict = getattr(params, params_attr)
        function_params = function_params_dict[selected_function]
        
        # Create unique attribute names for each group's header state
        group_state_prefix = f"{header_attr}_group_"
        
        # Display parameters by groups
        for i, group in enumerate(function_info.param_groups):
            
            # If group name is empty, display parameters directly under the main header
            if not group.display_name:
                for param_info in group.params:
                    param_control(param_info, function_params, header)
                continue
            
            group_state_attr = f"{group_state_prefix}{i}"
            if not hasattr(ui_state, group_state_attr):
                setattr(ui_state, group_state_attr, True)  # Initialize group state if not exists
            
            if ih.collapsing_header(group.display_name, ui_state, attr=group_state_attr, flags=imgui.TREE_NODE_DEFAULT_OPEN):
                for param_info in group.params:
                    param_control(param_info, function_params, header)


def param_control(param_info: FunctionParam, function_params: Dict, header: str):
    """Display the appropriate control for a parameter based on its type."""
    
    param_name = param_info.name
    
    match param_info.param_type.name:
        case 'int':
            changed, new_value = imgui.slider_int(
                f"{param_info.display_name}##{header}", 
                function_params[param_name], 
                param_info.min, 
                param_info.max
            )
            if changed:
                function_params[param_name] = new_value
        
        case 'float':
            changed, new_value = imgui.slider_float(
                f"{param_info.display_name}##{header}", 
                function_params[param_name], 
                param_info.min, 
                param_info.max,
                flags=imgui.SLIDER_FLAGS_LOGARITHMIC if getattr(param_info, 'logarithmic', False) else 0
            )
            if changed:
                function_params[param_name] = new_value
        
        case 'color':
            changed, new_value = imgui.color_edit4(
                f"{param_info.display_name}##{header}",
                *function_params[param_name],
                flags=imgui.COLOR_EDIT_FLOAT | imgui.COLOR_EDIT_ALPHA_BAR
            )
            if changed:
                function_params[param_name] = list(new_value)
        
        case _:
            raise ValueError(f"Unsupported parameter type: {param_info.param_type}")
    
    if (description := getattr(param_info, 'description', None)):
        ih.show_tooltip(description)


def confirm_dialog(message: str, title: str) -> bool:
    """
    Displays a confirmation dialog with a message and Yes/No buttons.

    Args:
        message (str): The message to display in the dialog.
        title (str): The title of the dialog window.

    Returns:
        bool: True if user clicked Yes, False otherwise.
    """
    user_confirmed = False

    if imgui.begin_popup_modal(title, flags=imgui.WINDOW_ALWAYS_AUTO_RESIZE)[0]:
        imgui.spacing()
        imgui.text(f'{Icons.WARNING} {message}')
        imgui.spacing()

        if imgui.button("Yes"):
            user_confirmed = True
            imgui.close_current_popup()

        imgui.same_line()
        if imgui.button("No"):
            imgui.close_current_popup()

        imgui.end_popup()

    return user_confirmed


def open_folder_button(directory: Path):
    """
    Creates a button that opens the specified directory in the system's file explorer.

    Args:
        directory (Path): Directory to open
    """
    if imgui.button("Open Folder"):
        try:
            if platform.system() == "Windows":
                os.startfile(directory)
            elif platform.system() == "Darwin":  # macOS
                os.system(f'open "{directory}"')
            else:  # Assume Linux
                os.system(f'xdg-open "{directory}"')
        except Exception as e:
            logging.error(f"Failed to open directory: {e}")
