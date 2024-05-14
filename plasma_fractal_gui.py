import datetime
import logging
import math
import os
from pathlib import Path
import platform
from typing import *
import imgui

from mylib.config.config_path_manager import ConfigPathManager
from mylib.config.json_file_storage import JsonFileStorage
from mylib.config.source_manager import StorageSourceManager
from mylib.function_registry import FunctionRegistry
from mylib.icons import Icons
from mylib.notification_manager import NotificationManager
from mylib.window_fade_manager import WindowFadeManager
from plasma_fractal_params import BlendFunctionRegistry, NoiseAlgorithm, PlasmaFractalParams, WarpFunctionRegistry
import mylib.imgui_helper as ih
from mylib.adjust_color import modify_rgba_color_hsv

from enum import Enum, auto

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


    def __init__(self, path_manager: ConfigPathManager):
     
        self.animation_paused = False
        
        self.noise_settings_open = True
        self.fractal_settings_open = True
        self.output_settings_open = True
        self.feedback_general_settings_open = True
        self.feedback_warp_noise_settings_open = True
        self.feedback_warp_octave_settings_open = True
        self.feedback_warp_effect_settings_open = True

        self.preset_list = []
        self.selected_preset_index = -1
        self.current_preset_name = "new_file"

        self.app_presets_directory = os.path.join(path_manager.app_specific_path, 'presets')
        self.user_presets_directory = os.path.join(path_manager.user_specific_path, 'presets')
        self.preset_error_message = None
        
        self.app_storage     = JsonFileStorage(self.app_presets_directory)
        self.user_storage    = JsonFileStorage(self.user_presets_directory)
        self.storage_manager = StorageSourceManager(self.app_storage, self.user_storage)        

        # Initialize recording state
        self.is_recording = False
        self.recording_directory = None
        self.recording_file_name = f"Capture_{datetime.datetime.now().strftime('%y%m%d_%H%M')}.mp4"
        self.recording_last_saved_file_path = None
        self.recording_resolution = 'HD 720p'
        self.recording_width = None
        self.recording_height = None
        self.recording_fps = 60
        self.recording_duration = 30
        self.recording_time = None
        self.recording_error_message = None

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
                self.fade_manager.update(imgui.get_mouse_pos(), imgui.get_window_position(), imgui.get_window_size())

                # Display the current FPS value
                if self.actual_fps:
                    # Set color according to the difference between actual and desired FPS                   
                    tolerance = 0.05 * self.desired_fps
                    color = (0.2, 1.0, 0.2) if abs(self.actual_fps - self.desired_fps) <= tolerance else (1.0, 0.9, 0.2)
                    imgui.text_colored(f"FPS: {self.actual_fps:.0f}", *color)
                    imgui.spacing()

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

                        with imgui.begin_tab_item("Feedback") as feedback_tab:
                            if feedback_tab.selected:
                                self.handle_feedback_tab(params)

                        with imgui.begin_tab_item("Presets") as presets_tab:
                            if presets_tab.selected:
                                self.handle_presets_tab(params)

                        with imgui.begin_tab_item("Recording") as recording_tab:
                            if recording_tab.selected:
                                self.handle_recording_tab(params)
    

    def handle_noise_tab(self, params: PlasmaFractalParams):
        """
        Manages the UI controls for adjusting noise-related settings in the plasma fractal visualization.

        Args:
            params (PlasmaFractalParams): The current settings of the plasma fractal that can be adjusted via the UI.
        """
        with ih.resized_items(-160):

            if ih.collapsing_header("Noise Settings", self, attr='noise_settings_open'):
                ih.slider_float("Scale", params, 'scale', min_value=0.01, max_value=100.0, flags=imgui.SLIDER_FLAGS_LOGARITHMIC)
                ih.enum_combo("Noise Algorithm", params, 'noise_algorithm')

            if ih.collapsing_header("Fractal Settings", self, attr='fractal_settings_open'):
                ih.slider_int("Num. Octaves", params, 'octaves', min_value=1, max_value=12)
                ih.slider_float("Gain/Octave", params, 'gain', min_value=0.1, max_value=1.0)
                ih.slider_float("Pos. Scale/Octave", params, 'positionScaleFactor', min_value=0.1, max_value=10.0)
                ih.slider_float("Rotation/Octave", params, 'rotationAngleIncrement', min_value=0.0, max_value=math.pi * 2, flags=imgui.SLIDER_FLAGS_LOGARITHMIC)
                ih.slider_float("Time Scale/Octave", params, 'timeScaleFactor', min_value=0.1, max_value=2.0)
                ih.slider_float("Time Offset/Octave", params, 'timeOffsetIncrement', min_value=0.0, max_value=20.0)

            if ih.collapsing_header("Output Settings", self, attr='output_settings_open'):
                ih.slider_float("Brightness", params, 'brightness', min_value=0.0, max_value=2.0)
                ih.slider_float("Contrast", params, 'contrastSteepness', min_value=0.001, max_value=50.0)
                ih.slider_float("Contrast Midpoint", params, 'contrastMidpoint', min_value=0.0, max_value=1.0)


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
                                   registry=BlendFunctionRegistry, function_attr='feedback_function', params_attr='feedback_params', 
                                   params=params)
      
            if ih.collapsing_header("Warp Noise Settings", self, attr='feedback_warp_noise_settings_open'):

                ih.slider_float("Speed", params, 'warpSpeed', min_value=0.01, max_value=10.0)
                ih.slider_float("Scale", params, 'warpScale', min_value=0.01, max_value=10.0)
                ih.enum_combo("Noise Algorithm", params, 'warpNoiseAlgorithm')

            if ih.collapsing_header("Warp Fractal Settings", self, attr='feedback_warp_octave_settings_open'):

                ih.slider_int("Num. Octaves", params, 'warpOctaves', min_value=1, max_value=12)
                ih.slider_float("Gain/Octave", params, 'warpGain', min_value=0.1, max_value=1.0)
                ih.slider_float("Pos. Scale/Octave", params, 'warpPositionScaleFactor', min_value=0.1, max_value=10.0)
                ih.slider_float("Rotation/Octave", params, 'warpRotationAngleIncrement', min_value=0.0, max_value=math.pi * 2, flags=imgui.SLIDER_FLAGS_LOGARITHMIC)
                ih.slider_float("Time Scale/Octave", params, 'warpTimeScaleFactor', min_value=0.1, max_value=2.0)
                ih.slider_float("Time Offset/Octave", params, 'warpTimeOffsetIncrement', min_value=0.0, max_value=20.0)

            self.function_settings(header="Warp Function Settings", header_attr='feedback_warp_effect_settings_open', 
                                   registry=WarpFunctionRegistry, function_attr='warpFunction', params_attr='warpParams',
                                   params=params)


    def function_settings(self, 
                          header: str, 
                          header_attr: str, 
                          registry: FunctionRegistry,
                          function_attr: str,
                          params_attr: str,
                          params: PlasmaFractalParams):
        """
        Display the settings for a specific function.

        Args:
            header (str): The header text to display for the collapsible section.
            header_attr (str): The attribute name in the object to store the collapsed state.
            registry (FunctionRegistry): The registry of available functions.
            function_attr (str): The attribute name in the object to store the selected function.
            params (PlasmaFractalParams): The object containing the overall parameters.

        Returns:
            None
        """
        if ih.collapsing_header(header, self, attr=header_attr):
            
            # Dropdown for the available functions
            # Make sure to create a unique identifier by appending the header to the label
            ih.enum_combo(f"Function##{header}", obj=params, attr=function_attr)
            
            selected_function = getattr(params, function_attr)
            
            # Get the current function info
            function_info = registry.get_function_info(selected_function)
            
            # Get the parameters for the selected function
            function_params_dict = getattr(params, params_attr)
            function_params = function_params_dict[selected_function.name] 
            
            # Generate sliders for the function's parameters
            for index, param_info in enumerate(function_info.params):

                changed, new_value = imgui.slider_float(f"{param_info.display_name}##{header}", 
                                                        function_params[index], 
                                                        param_info.min, 
                                                        param_info.max, 
                                                        flags=imgui.SLIDER_FLAGS_LOGARITHMIC if param_info.logarithmic else 0)
                if changed:
                    function_params[index] = new_value


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
                
                display_name = f"* {preset.name}" if preset.source == StorageSourceManager.Source.APP else preset.name
                
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
        confirm_dlg_title = "Confirm Overwrite"

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

            logging.info(f"Confirmed to overwrite existing preset: {self.current_preset_name}")
            self.save_preset(params)


    def preset_delete_ui(self, params: PlasmaFractalParams):
        """
        Handles the logic for deleting a preset.
        """
        # Make sure we don't delete predefined presets, only user-defined ones
        if self.get_current_preset().source == StorageSourceManager.Source.USER:

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
            storage = self.storage_manager.get_storage(current_preset.source)
            self.open_folder(storage.directory)


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
        self.preset_list = self.storage_manager.list_items()
        
        self.selected_preset_index = -1


    def apply_preset(self, params: PlasmaFractalParams, selected_preset: StorageSourceManager.Item):
        """
        Loads the preset data from a file and updates the current fractal parameters accordingly.

        Args:
            params (PlasmaFractalParams): The fractal parameters to be updated.
            selected_preset (StorageSourceManager.Item): The preset selected by the user for application.
        """
        self.preset_error_message = None

        try:
            storage = self.storage_manager.get_storage(selected_preset.source)          
            preset_data = storage.load(selected_preset.name)
            
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

        try:
            logging.debug(f'Saving preset: "{self.current_preset_name}" to "{self.user_presets_directory}"')
            
            data = params.to_dict()
            self.user_storage.save(data, self.current_preset_name)

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
                ih.input_int("Width", self, 'recording_width', step=1, step_fast=10)
                ih.input_int("Height", self, 'recording_height', step=1, step_fast=10)
            else:
                # Update resolution from predefined resolutions
                self.recording_width, self.recording_height = common_resolutions[self.recording_resolution]

            # Frame rates combo box
            common_frame_rates = [24, 30, 60, 120]
            ih.list_combo("Frame Rate", obj=self, attr='recording_fps', items=common_frame_rates)

            # Recording Duration input
            imgui.spacing()
            ih.input_int("Duration (sec)", self, 'recording_duration', step=1, step_fast=10)
            if self.recording_duration < 0:
                self.recording_duration = 0

            # Start/Stop recording toggle button
            imgui.spacing()
            if imgui.button("Start Recording" if not self.is_recording else "Stop Recording"):
                self.start_recording() if not self.is_recording else self.stop_recording()

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

    def start_recording(self):

        self.is_recording = True
        self.recording_error_message = None
        self.recording_last_saved_file_path = None
        self.notifications.push_notification(self.Notification.RECORDING_STATE_CHANGED, {'is_recording': self.is_recording})

    def stop_recording(self):

        self.is_recording = False
        self.recording_last_saved_file_path = os.path.join(self.recording_directory, self.recording_file_name)
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

