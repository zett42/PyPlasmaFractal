﻿from enum import Enum, auto
import datetime
import logging
import math
import os
from pathlib import Path
import platform
from typing import *
import imgui
 
from PyPlasmaFractal.mylib.config.config_path_manager import ConfigPathManager
from PyPlasmaFractal.mylib.config.function_info import FunctionParam
from PyPlasmaFractal.mylib.config.json_file_storage import JsonFileStorage
from PyPlasmaFractal.mylib.config.source_manager import StorageSourceManager
from PyPlasmaFractal.mylib.config.function_registry import FunctionRegistry, ParamType
from PyPlasmaFractal.mylib.gui.ansi_style import AnsiStyle
from PyPlasmaFractal.mylib.gui.icons import Icons
from PyPlasmaFractal.mylib.gui.notification_manager import NotificationManager
from PyPlasmaFractal.mylib.gui.window_fade_manager import WindowFadeManager
import PyPlasmaFractal.mylib.gui.imgui_helper as ih
from PyPlasmaFractal.mylib.color.adjust_color import modify_rgba_color_hsv, sigmoid_contrast
from PyPlasmaFractal.plasma_fractal_types import ShaderFunctionType
from .plasma_fractal_params import PlasmaFractalParams

class PlasmaFractalGUI:
    """
    Manages the user interface for PyPlasmaFractal.
      
    Attributes:
        preset_list (List[Preset]): A list of available presets, populated on-demand.
        selected_preset_index (int): The index of the currently selected preset in the list.
        animation_paused (bool): Flag to indicate whether the animation is paused.
        noise_settings_open (bool): Flag to control the visibility of the noise settings.
        fractal_settings_open (bool): Flag to control the visibility of fractal settings.
        output_settings_open (bool): Flag to control the visibility of output settings.
        feedback_general_settings_open (bool): Flag to control the visibility of general feedback settings.
        feedback_warp_noise_settings_open (bool): Flag to control the visibility of feedback noise settings.
        feedback_warp_octave_settings_open (bool): Flag to control the visibility of feedback octave settings.
        feedback_warp_effect_settings_open (bool): Flag to control the visibility of feedback effect settings.
    """

    # Notification types for the notification manager

    class Notification(Enum):
        NEW_PRESET_LOADED = auto()         # Send by the GUI when a new preset is loaded
        RECORDING_STATE_CHANGED = auto()   # Send by the GUI when the recording state changes
        RECORDING_ERROR = auto()           # Received by the GUI when an error occurs during recording
        LOAD_CONFIG_ERROR = auto()         # Received by the GUI when an error occurs while loading the configuration

    def __init__(self, path_manager: ConfigPathManager, 
                 function_registries: Dict[ShaderFunctionType, FunctionRegistry],
                 recording_directory: Union[Path, str], 
                 default_recording_fps: int):
     
        self.noise_function_registry = function_registries[ShaderFunctionType.NOISE]
        self.blend_function_registry = function_registries[ShaderFunctionType.BLEND]
        self.warp_function_registry  = function_registries[ShaderFunctionType.WARP]
        self.color_function_registry = function_registries[ShaderFunctionType.COLOR]
     
        self.animation_paused = False
        
        # Initialize the visibility state for the different settings tabs
        self.noise_settings_open = True
        self.output_settings_open = True
        self.feedback_general_settings_open = True
        self.feedback_blur_settings_open = True
        self.feedback_warp_noise_settings_open = True
        self.feedback_warp_effect_settings_open = True
        self.feedback_color_adjustment_open = True
        self.color_function_settings_open = True

        # Initialize preset management
        self.preset_list = []
        self.selected_preset_index = -1
        self.current_preset_name = "new_file"
        self.preset_error_message = None
        self.preset_last_saved_file_path = None
        self.app_storage     = JsonFileStorage(Path(path_manager.app_specific_path)  / 'presets', list_extension=False)
        self.user_storage    = JsonFileStorage(Path(path_manager.user_specific_path) / 'presets', list_extension=False)
        self.storage_manager = StorageSourceManager(self.app_storage, self.user_storage)        

        # Initialize recording state
        self.recording_directory = Path(recording_directory)
        self.recording_file_name = f"Capture_{datetime.datetime.now().strftime('%y%m%d_%H%M')}.mp4"
        self.recording_fps = default_recording_fps
        self.recording_last_saved_file_path = None
        self.recording_resolution = 'HD 720p'
        self.recording_width = None
        self.recording_height = None
        self.recording_fps = 60
        self.recording_duration = 30
        self.recording_quality = 8
        self.recording_time = None
        self.recording_error_message = None
        self.is_recording = False

        # FPS display
        self.actual_fps = 0.0
        self.desired_fps = 0.0

        # Initialize the fade manager for the control panel
        self.fade_manager = WindowFadeManager()

        # Initialize the notification manager
        self.notifications = NotificationManager[self.Notification]()


    # .......................... UI update methods ...........................................................................

    def update(self, params: PlasmaFractalParams):
        """
        Updates the UI elements in the control panel for managing plasma fractal visualization settings.

        This method handles the layout and interaction logic for the control panel, organizing settings into
        tabs. It allows users to modify plasma fractal parameters directly through graphical controls like sliders and checkboxes.

        Args:
            params (PlasmaFractalParams): The current settings of the plasma fractal that can be adjusted via the UI.
        """
        style = imgui.get_style()
        new_hdr_color = modify_rgba_color_hsv(style.colors[imgui.COLOR_HEADER], -0.05, 1.0, 1.0)

        with imgui.styled(imgui.STYLE_ALPHA, self.fade_manager.alpha), imgui.colored(imgui.COLOR_HEADER, *new_hdr_color):

            imgui.set_next_window_size(400, 800, imgui.FIRST_USE_EVER)
            with imgui.begin("Control Panel"):

                # Fade the control panel in or out based on mouse activity
                self.fade_manager.update(imgui.get_mouse_pos(), imgui.is_window_focused(imgui.FOCUS_ANY_WINDOW))

                # Display the "Reset to Defaults" button and handle the confirmation dialog
                self.show_reset_button_and_confirm_dialog(params)

                # Display the current FPS in the same line as the "Reset to Defaults" button
                self.display_fps_same_line()

                width = imgui.get_content_region_available_width()

                imgui.set_next_item_width(width - 160)
                ih.slider_float("Speed", params, 'speed', min_value=0.01, max_value=10.0, flags=imgui.SLIDER_FLAGS_LOGARITHMIC)

                imgui.same_line()
                ih.checkbox("Paused", self, attr='animation_paused')
                imgui.spacing()

                with imgui.begin_tab_bar("Control Tabs") as tab_bar:
                    if tab_bar.opened:
                        with imgui.begin_tab_item("Noise") as noise_tab:
                            if noise_tab.selected:
                                self.handle_noise_tab(params)

                        with imgui.begin_tab_item("Color") as color_tab:
                            if color_tab.selected:
                                self.handle_color_tab(params)

                        with imgui.begin_tab_item("Feedback") as feedback_tab:
                            if feedback_tab.selected:
                                self.handle_feedback_tab(params)

                        with imgui.begin_tab_item("Presets") as presets_tab:
                            if presets_tab.selected:
                                self.handle_presets_tab(params)

                        with imgui.begin_tab_item("Recording") as recording_tab:
                            if recording_tab.selected:
                                self.handle_recording_tab(params)

    
    def show_reset_button_and_confirm_dialog(self, params: PlasmaFractalParams):
        """
        Displays the "Reset to Defaults" button and handles the confirmation dialog.

        Args:
            params (PlasmaFractalParams): The parameters of the plasma fractal.
        """
        confirm_dialog_title = "Confirm Reset"
        
        if imgui.button("Reset to Defaults"):
            imgui.open_popup(confirm_dialog_title)

        if self.confirm_dialog("Are you sure you want to reset all settings to their defaults?", confirm_dialog_title):
            params.apply_defaults()
            self.notifications.push_notification(self.Notification.NEW_PRESET_LOADED)
    
    
    def display_fps_same_line(self):
        """
        Displays the current FPS in the same line as the "Reset to Defaults" button, right-aligned to the content area
        and color-coded based on the difference between actual and desired FPS.
        """
        if self.actual_fps:
            tolerance = 0.05 * self.desired_fps
            color = (0.2, 1.0, 0.2) if abs(self.actual_fps - self.desired_fps) <= tolerance else (1.0, 0.9, 0.2)
            fps_text = f"FPS: {self.actual_fps:.0f}"
        else:
            color = (1.0, 0.9, 0.2)
            fps_text = "FPS: N/A"
        
        content_width = imgui.get_content_region_available_width()
        fps_text_width = imgui.calc_text_size(fps_text)[0]

        # Add spacing to align FPS text to the right
        imgui.same_line(content_width - fps_text_width)
        imgui.text_colored(fps_text, *color)
          
        imgui.spacing()                
            

    def handle_noise_tab(self, params: PlasmaFractalParams):
        """
        Manages the UI controls for adjusting noise-related settings in the plasma fractal visualization.

        Args:
            params (PlasmaFractalParams): The current settings of the plasma fractal that can be adjusted via the UI.
        """
               
        with ih.resized_items(-160):

            if ih.collapsing_header("Noise Settings", self, attr='noise_settings_open'):
                self.noise_controls(params.noise, 'noise')

            if ih.collapsing_header("Output Settings", self, attr='output_settings_open'):
                
                ih.slider_float("Brightness", params, 'brightness', min_value=0.0, max_value=2.0)
                ih.show_tooltip("Adjust the brightness of the rendered noise.\n"
                                "Higher values increase the overall intensity of the noise pattern.")
                
                ih.slider_float("Contrast", params, 'contrast_steepness', min_value=0.001, max_value=50.0)
                ih.show_tooltip("Set the contrast steepness of the rendered noise.\n"
                                "Higher values result in sharper contrasts between light and dark areas.")
                
                ih.slider_float("Contrast Midpoint", params, 'contrast_midpoint', min_value=0.0, max_value=1.0)
                ih.show_tooltip("Adjust the midpoint for contrast adjustments.\n"
                                "Higher values shift the midpoint towards the brighter end of the intensity range.")

                ih.plot_callable('##output_curve', 
                                 lambda x: sigmoid_contrast(x, params.contrast_steepness, params.contrast_midpoint) * params.brightness, 
                                 scale_max=2.0)


    def handle_feedback_tab(self, params: PlasmaFractalParams):
        """
        Manages the UI controls for the feedback settings in the plasma fractal visualization.

        Args:
            params (PlasmaFractalParams): The current settings of the plasma fractal, which include feedback-related parameters.
        """
        ih.checkbox("Enable Feedback", params, 'enable_feedback')

        if params.enable_feedback:
            imgui.spacing()
            self.handle_feedback_controls(params)
        else:
            imgui.spacing()
            imgui.spacing()
            imgui.text_colored("Note", 1.0, 0.9, 0.2)
            imgui.separator()
            imgui.text_wrapped("After enabling feedback, you might want to adjust the noise settings, particularly the contrast for better results.")


    def handle_feedback_controls(self, params: PlasmaFractalParams):
        """
        Manages detailed UI controls for configuring feedback effects in the plasma fractal visualization.

        Args:
            params (PlasmaFractalParams): The current settings of the plasma fractal, specifically for configuring feedback effects.
        """
        with ih.resized_items(-160):

            self.function_settings(header="Feedback Mix Settings", header_attr='feedback_general_settings_open', 
                                   registry=self.blend_function_registry, function_attr='feedback_function', params_attr='feedback_params', 
                                   params=params)

            if ih.collapsing_header("Feedback Blur Settings", self, attr='feedback_blur_settings_open'):
                                   
                ih.checkbox("Enable Blur", params, 'enable_feedback_blur')
                if params.enable_feedback_blur:
                    ih.slider_int("Blur Radius", params, 'feedback_blur_radius', min_value=1, max_value=16)
                    ih.slider_float("Blur Radius Power", params, 'feedback_blur_radius_power', min_value=0.01, max_value=20, flags=imgui.SLIDER_FLAGS_LOGARITHMIC)
      
            if ih.collapsing_header("Warp Noise Settings", self, attr='feedback_warp_noise_settings_open'):
                self.noise_controls(params.warp_noise, 'warp_noise')

            self.function_settings(header="Warp Function Settings", header_attr='feedback_warp_effect_settings_open', 
                                   registry=self.warp_function_registry, function_attr='warp_function', params_attr='warp_params',
                                   params=params)


    def noise_controls(self, noise_params, unique_id: str):
        """
        Creates the GUI controls for noise parameters.

        Args:
            noise_params: The noise parameters object to modify
            unique_id: Used to create unique control IDs
        """
        self.function_combo(f"Noise Algorithm##{unique_id}", noise_params, 'noise_algorithm', self.noise_function_registry)

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


    def handle_color_tab(self, params: PlasmaFractalParams):
        """
        Manages the UI controls for adjusting color-related settings in the plasma fractal visualization.

        Args:
            params (PlasmaFractalParams): The current settings of the plasma fractal that can be adjusted via the UI.
        """
              
        with ih.resized_items(-160):

            self.function_settings(header="Color Function Settings", header_attr='color_function_settings_open', 
                                    registry=self.color_function_registry, function_attr='color_function', params_attr='color_params', 
                                    params=params)


    def function_combo(self, combo_label: str, params: PlasmaFractalParams, params_attr: str, registry: FunctionRegistry):
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

        # Unzip the sorted tuples into separate lists
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
        

    def function_settings(self, 
                         header: str, 
                         header_attr: str, 
                         registry: FunctionRegistry,
                         function_attr: str,
                         params_attr: str,
                         params: PlasmaFractalParams):
        
        """Display the setting controls for a specific function."""
        
        if ih.collapsing_header(header, self, attr=header_attr):
            
            # Dropdown for the available functions 
            self.function_combo(f"Function##{function_attr}", params, function_attr, registry)        
                      
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
                        self.param_control(param_info, function_params, header)
                    continue
                
                group_state_attr = f"{group_state_prefix}{i}"
                if not hasattr(self, group_state_attr):
                    setattr(self, group_state_attr, True)  # Initialize group state if not exists
                
                if ih.collapsing_header(group.display_name, self, attr=group_state_attr, flags=imgui.TREE_NODE_DEFAULT_OPEN):
                    for param_info in group.params:
                        self.param_control(param_info, function_params, header)


    def param_control(self, param_info: FunctionParam, function_params: Dict, header: str):
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


    def handle_presets_tab(self, params: PlasmaFractalParams):
        """
        Manages the presets tab in the UI, allowing users to load, apply, and save presets for plasma fractal configurations.

        Args:
            params (PlasmaFractalParams): The fractal parameters that can be modified by applying a preset.
        """

        # Fetch the initial list of presets if it hasn't been done yet
        if not self.preset_list:
            self.update_presets_list()

        self.preset_selection_ui(params)

        if self.selected_preset_index >= 0:
            # Controls that depend on a selected preset
            imgui.spacing()
            self.preset_load_ui(params)
            imgui.same_line()
            self.preset_delete_ui(params)
            imgui.same_line()
            self.presets_open_folder_ui()
        
        imgui.spacing()
        self.preset_save_ui(params)

        self.handle_preset_error()


    def preset_selection_ui(self, params: PlasmaFractalParams):
        """
        Displays the available presets in a list box.

        Returns:
            None
        """
        width = imgui.get_content_region_available_width()

        imgui.spacing()
        imgui.text("Available Presets (* marks built-ins):")
        imgui.spacing()

        if imgui.begin_list_box("##AvailablePresets", width, 450):
            
            for i, preset in enumerate(self.preset_list):
                
                display_name = f"* {preset.name}" if preset.storage == self.storage_manager.app_storage else preset.name
                
                opened, _ = imgui.selectable(display_name, self.selected_preset_index == i, flags=imgui.SELECTABLE_ALLOW_DOUBLE_CLICK)

                if opened:
                    self.selected_preset_index = i
                    self.current_preset_name = preset.name

                    if imgui.is_mouse_double_clicked(0):
                        self.apply_preset(params, preset)

            imgui.end_list_box()



    def preset_load_ui(self, params):
        """
        Loads the selected preset and applies it to the given parameters.

        Args:
            params (dict): The parameters to apply the preset to.

        Returns:
            None
        """
        if imgui.button("Load"):
            current_preset = self.get_current_preset()
            if current_preset:
                self.apply_preset(params, current_preset)


    def preset_save_ui(self, params: PlasmaFractalParams):
        """
        Handles the logic for saving a preset.

        Args:
            params (PlasmaFractalParams): The parameters of the plasma fractal.

        Returns:
            None
        """
        confirm_dlg_title = "Confirm Overwrite Preset"

        # As we don't need a label, just specify an ID for the title.
        if ih.input_text("##PresetName", self, 'current_preset_name'):
            # Remove the extension from the file name
            self.current_preset_name = Path(self.current_preset_name).stem  

        imgui.same_line()

        if imgui.button("Save"):
            
            # If the preset already exists, trigger the confirmation dialog before saving
            if self.storage_manager.user_storage.exists(self.current_preset_name):
                imgui.open_popup(confirm_dlg_title)
            else:
                self.save_preset(params)

        # Shows the confirmation dialog if triggered by open_popup().
        # Note: this needs to be on the same level as the button, otherwise the popup won't work
        if self.confirm_dialog(f'A preset with this name already exists:\n"{self.current_preset_name}"\n\nDo you want to overwrite it?',
                               confirm_dlg_title):

            self.save_preset(params)
            
        if self.preset_last_saved_file_path:
            # Show the path where the preset was saved
            imgui.spacing()
            imgui.text_colored(f"Preset saved to:", 0.2, 1.0, 1.0)
            ih.display_trimmed_path_with_tooltip(self.preset_last_saved_file_path)            


    def preset_delete_ui(self, params: PlasmaFractalParams):
        """
        Handles the logic for deleting a preset.
        """
        # Make sure we don't delete predefined presets, only user-defined ones
        if self.get_current_preset().storage == self.storage_manager.user_storage:

            if imgui.button("Delete"):
                imgui.open_popup("Confirm Deletion")

            # Confirmation popup logic
            if self.confirm_dialog(f'Are you sure you want to delete the preset "{self.current_preset_name}" ?', "Confirm Deletion"):
                self.delete_selected_preset()
 

    def presets_open_folder_ui(self):
        """
        Opens the folder where the user presets are stored.
        """            
        if imgui.button("Open Folder"):
            current_preset = self.get_current_preset()
            self.open_folder(current_preset.storage.directory)


    def handle_preset_error(self):
        """
        Displays an error message if there was an issue with loading or saving a preset.
        """
        if self.preset_error_message:
            imgui.spacing()
            imgui.separator()
            imgui.push_text_wrap_pos()
            imgui.text_colored(f"ERROR: {self.preset_error_message}", 1.0, 0.2, 0.2)
            imgui.pop_text_wrap_pos()


    def open_folder(self, directory: str):
        """
        Opens the presets directory in the system's default file explorer.
        """
        try:
            if platform.system() == "Windows":
                os.startfile(directory)
            elif platform.system() == "Darwin":  # macOS
                os.system(f'open "{directory}"')
            else:  # Assume Linux
                os.system(f'xdg-open "{directory}"')
        except Exception as e:
            logging.error(f"Failed to open directory: {e}")
            

    def confirm_dialog(self, message: str, title: str) -> bool:
        """
        Displays a confirmation dialog with a message and buttons for the user to confirm or cancel.

        Args:
            message (str): The message to display in the dialog.
            id (str, optional): An optional identifier for the dialog. Defaults to None.
            title (str, optional): The title of the dialog. Defaults to "Confirm Overwrite".

        Returns:
            bool: True if the user confirmed, False otherwise.
        """

        user_confirmed = False  # Default to False unless user confirms

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


    #.......................... Preset file management methods ...........................................................................

    def get_current_preset(self) -> StorageSourceManager.Item:
        """
        Returns the currently selected preset, or None if no preset is selected.
        """
        return self.preset_list[self.selected_preset_index] if self.selected_preset_index >= 0 else None


    def update_presets_list(self):
        """
        Updates the internal list of presets from both app-specific and user-specific directories.
        """
        self.preset_list = self.storage_manager.list()
        
        self.selected_preset_index = -1


    def apply_preset(self, params: PlasmaFractalParams, selected_preset: StorageSourceManager.Item):
        """
        Loads the preset data from a file and updates the current fractal parameters accordingly.

        Args:
            params (PlasmaFractalParams): The fractal parameters to be updated.
            selected_preset (StorageSourceManager.Item): The preset selected by the user for application.
        """
        self.preset_error_message = None
        self.preset_last_saved_file_path = None

        try:
            preset_data = selected_preset.storage.load(selected_preset.name)
            
            params.apply_defaults()
            params.merge_dict(preset_data)

            self.notifications.push_notification(self.Notification.NEW_PRESET_LOADED)

            logging.info(f'Preset "{selected_preset.name}" applied successfully.')

        except Exception as e:
            self.preset_error_message = f"Failed to apply preset: {str(e)}"
            logging.error(self.preset_error_message)


    def save_preset(self, params: PlasmaFractalParams):
        """
        Saves the current plasma fractal settings as a preset file in the user-specific directory.

        Args:
            params (PlasmaFractalParams): The fractal parameters to save.
        """
        self.preset_error_message = None
        self.preset_last_saved_file_path = None

        try:
            storage = self.user_storage
            logging.info(f'Saving preset: "{self.current_preset_name}" to "{storage.directory}"')
            
            data = params.to_dict()
            storage.save(data, self.current_preset_name)
            
            self.preset_last_saved_file_path = storage.get_full_path( self.current_preset_name )
            
            self.update_presets_list()

        except Exception as e:
            self.preset_error_message = f"Failed to save preset: {str(e)}"
            logging.error(self.preset_error_message)


    def delete_selected_preset(self):
        """
        Deletes the selected preset from the filesystem and updates the UI.
        """
        assert self.selected_preset_index != -1, "No preset is selected."

        self.preset_error_message = None
        self.preset_last_saved_file_path = None

        try:
            self.user_storage.delete(self.get_current_preset().name)
        except Exception as e:
            self.preset_error_message = f"Failed to delete preset: {str(e)}"
            logging.error(self.preset_error_message)

        self.update_presets_list()


    #.......................... Recording methods ...........................................................................

    def handle_recording_tab(self, params: PlasmaFractalParams):

        imgui.spacing()

        with ih.resized_items(-120):

            available_width = imgui.get_content_region_available_width()

            # Filename input
            if ih.input_text("Filename", self, 'recording_file_name', buffer_size=256):
                # Add .mp4 extension if not present
                if not self.recording_file_name.lower().endswith('.mp4'):
                    self.recording_file_name += '.mp4'

            # Common video resolutions
            common_resolutions = {
                'HD 720p'      : (1280,  720),
                'Full HD 1080p': (1920, 1080),
                '2K'           : (2560, 1440),
                '4K UHD'       : (3840, 2160),
                '8K UHD'       : (7680, 4320),
                'Custom'       : None  # This will trigger custom resolution input
            }
            resolution_names = list(common_resolutions.keys())

            # Resolution combo box refactored to use list_combo helper
            ih.list_combo("Resolution", self, 'recording_resolution', items=resolution_names)

            if self.recording_resolution == 'Custom':
                # Input fields for custom resolution
                ih.input_int("Width", self, 'recording_width',  step=1, step_fast=10)
                ih.input_int("Height", self, 'recording_height', step=1, step_fast=10)
                self.recording_width = max(2, self.recording_width)
                self.recording_height = max(2, self.recording_height)
            else:
                # Update resolution from predefined resolutions
                self.recording_width, self.recording_height = common_resolutions[self.recording_resolution]

            # Frame rates combo box
            common_frame_rates = [24, 30, 60, 120]
            ih.list_combo("Frame Rate", obj=self, attr='recording_fps', items=common_frame_rates)
            
            # Recording quality input
            ih.slider_int("Quality", self, 'recording_quality', min_value=1, max_value=10)

            # Recording Duration input
            imgui.spacing()
            ih.input_int("Duration (sec)", self, 'recording_duration', step=1, step_fast=10)
            if self.recording_duration < 0:
                # Value of 0 means no limit (manual stop required)
                self.recording_duration = 0

            # Start/Stop recording toggle button
            self.handle_recording_button()

            # Automatic stop check
            self.handle_automatic_stop()

            # Display recording time if recording
            if self.is_recording and self.recording_time is not None:
                imgui.spacing()
                recording_time_str = self.convert_seconds_to_hms(self.recording_time)
                imgui.text_colored(f"Recording... {recording_time_str}", 1.0, 0.2, 1.0)

            # Check for recording errors
            if (message := self.notifications.pull_notification(self.Notification.RECORDING_ERROR)) is not None:
                self.is_recording = False
                self.recording_error_message = message

            if not self.is_recording:
                imgui.spacing()
                imgui.separator()

                if self.recording_error_message:
                    # Show error message if recording failed
                    imgui.spacing()
                    imgui.spacing()
                    imgui.push_text_wrap_pos()
                    imgui.text_colored(f"ERROR: {self.recording_error_message}", 1.0, 0.2, 0.2)
                    imgui.pop_text_wrap_pos()
                    imgui.separator()

                elif self.recording_last_saved_file_path:
                    # Show the path where the recording was saved
                    imgui.spacing()
                    imgui.text_colored(f"Recording saved to:", 0.2, 1.0, 1.0)
                    ih.display_trimmed_path_with_tooltip(self.recording_last_saved_file_path, available_width)

                # Add a button to open the video folder
                if not self.is_recording:
                    imgui.spacing()
                    if imgui.button("Open Folder"):
                        self.open_folder(self.recording_directory)
                        
    def handle_recording_button(self):
        """
        Checks if the recording file already exists and shows a confirmation dialog if it does.
        """
        dialog_title = "Confirm Overwrite Recording"

        imgui.spacing()
        if imgui.button("Start Recording" if not self.is_recording else "Stop Recording"):           
            if self.is_recording:
                self.stop_recording()
                return
            
            if (Path(self.recording_directory) / self.recording_file_name).exists():
                imgui.open_popup(dialog_title)
            else:
                self.start_recording()

        if self.confirm_dialog(f'A recording with this name already exists:\n"{self.recording_file_name}"\n\nDo you want to overwrite it?',
                               dialog_title):
            logging.info(f"Confirmed to overwrite existing recording file: {self.recording_file_name}")
            self.start_recording()                  

    def start_recording(self):

        self.is_recording = True
        self.recording_error_message = None
        self.recording_last_saved_file_path = None
        self.notifications.push_notification(self.Notification.RECORDING_STATE_CHANGED, {'is_recording': self.is_recording})

    def stop_recording(self):

        self.is_recording = False
        self.recording_last_saved_file_path = self.recording_directory / self.recording_file_name
        self.notifications.push_notification(self.Notification.RECORDING_STATE_CHANGED, {'is_recording': self.is_recording})

    def handle_automatic_stop(self):

        if self.is_recording and self.recording_time is not None and self.recording_duration > 0:
            if self.recording_time >= self.recording_duration:
                self.stop_recording()

    @staticmethod
    def convert_seconds_to_hms(seconds: Union[int, float]) -> str:
        seconds = int(seconds)  # Ensure seconds are whole numbers
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

