﻿import datetime
import logging
import math
import os
import platform
from typing import *
import imgui

from mylib.config_path_manager import ConfigPathManager
from mylib.icons import Icons
from mylib.window_fade_manager import WindowFadeManager
from plasma_fractal_params import PlasmaFractalParams, WarpFunctionRegistry
import mylib.imgui_helper as ih
from mylib.adjust_color import modify_rgba_color_hsv
from mylib.presets_manager import Preset
import mylib.presets_manager as presets_manager

#------------------------------------------------------------------------------------------------------------------------------------

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
        self.new_preset_loaded = False

        self.app_presets_directory = os.path.join(path_manager.app_specific_path, 'presets')
        self.user_presets_directory = os.path.join(path_manager.user_specific_path, 'presets')

        logging.debug(f"App presets directory: {self.app_presets_directory}")
        logging.debug(f"User presets directory: {self.user_presets_directory}")

        # Initialize recording state
        self.is_recording = False
        self.recording_directory = None
        self.recording_file_name = f"Capture_{datetime.datetime.now().strftime('%y%m%d_%H%M')}.mp4"
        self.recording_resolution = 'HD 720p'
        self.recording_width = None
        self.recording_height = None
        self.recording_fps = 60
        self.recording_duration = 30
        self.recording_time = None

        # FPS display
        self.actual_fps = 0.0
        self.desired_fps = 0.0

        # Initialize the fade manager for the control panel
        self.fade_manager = WindowFadeManager()


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

            if ih.collapsing_header("Feedback Mix Settings", self, attr='feedback_general_settings_open'):
                #Slider for feedback blend mode
                ih.enum_combo("Blend Mode", params, 'feedback_blend_mode')
                ih.slider_float("Feedback Decay", params, 'feedback_decay', min_value=0, max_value=1.0, flags=imgui.SLIDER_FLAGS_LOGARITHMIC)
                ih.slider_float("Feedback Param 1", params, 'feedback_param1', min_value=0, max_value=1.0, flags=imgui.SLIDER_FLAGS_LOGARITHMIC)
                ih.slider_float("Feedback Param 2", params, 'feedback_param2', min_value=0, max_value=1.0)

            if ih.collapsing_header("Feedback Noise Settings", self, attr='feedback_warp_noise_settings_open'):
                ih.slider_float("Speed", params, 'warpSpeed', min_value=0.01, max_value=10.0)
                ih.slider_float("Scale", params, 'warpScale', min_value=0.01, max_value=10.0)
                ih.enum_combo("Noise Algorithm", params, 'warpNoiseAlgorithm')

            if ih.collapsing_header("Feedback Fractal Settings", self, attr='feedback_warp_octave_settings_open'):
                ih.slider_int("Num. Octaves", params, 'warpOctaves', min_value=1, max_value=12)
                ih.slider_float("Gain/Octave", params, 'warpGain', min_value=0.1, max_value=1.0)
                ih.slider_float("Pos. Scale/Octave", params, 'warpPositionScaleFactor', min_value=0.1, max_value=10.0)
                ih.slider_float("Rotation/Octave", params, 'warpRotationAngleIncrement', min_value=0.0, max_value=math.pi * 2, flags=imgui.SLIDER_FLAGS_LOGARITHMIC)
                ih.slider_float("Time Scale/Octave", params, 'warpTimeScaleFactor', min_value=0.1, max_value=2.0)
                ih.slider_float("Time Offset/Octave", params, 'warpTimeOffsetIncrement', min_value=0.0, max_value=20.0)

            if ih.collapsing_header("Feedback Effect Settings", self, attr='feedback_warp_effect_settings_open'):
                ih.list_combo("Warp Function", params, 'warpFunction', items=WarpFunctionRegistry.get_all_function_names())

                for index, paramInfo in enumerate(params.get_current_warp_function_info().params):

                    label = f"{paramInfo.displayName}##{params.warpFunction}"
                    ih.slider_float(label, params.get_current_warp_params(), index=index,
                                    min_value=paramInfo.min, max_value=paramInfo.max, 
                                    flags=imgui.SLIDER_FLAGS_LOGARITHMIC if paramInfo.logarithmic else 0)


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
            self.presets_open_folder_ui(params)
        
        imgui.spacing()
        self.preset_save_ui(params)


    def preset_selection_ui(self, params: PlasmaFractalParams):
        """
        Displays the available presets in a list box.

        Parameters:
        - width (int): The width of the list box.

        Returns:
        None
        """
        width = imgui.get_content_region_available_width()

        imgui.spacing()
        imgui.text("Available Presets (* marks built-ins):")
        imgui.spacing()

        if imgui.begin_list_box("##AvailablePresets", width, 450):

            for i, preset in enumerate(self.preset_list):

                # Remove the file extension from the display name
                base_name, _ = os.path.splitext(preset.relative_file_path)
                display_name = f"* {base_name}" if preset.is_predefined else base_name

                opened, _ = imgui.selectable(display_name, self.selected_preset_index == i, flags=imgui.SELECTABLE_ALLOW_DOUBLE_CLICK)

                if opened:
                    self.selected_preset_index = i
                    self.current_preset_name = base_name

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
            self.current_preset_name, _ = os.path.splitext(self.current_preset_name)  

        imgui.same_line()

        if imgui.button("Save"):
            
            full_path = self.get_full_preset_path(self.current_preset_name)
            preset_exists = os.path.exists(full_path)

            if preset_exists:
                # If the preset already exists, show a confirmation dialog before saving
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
        if not self.get_current_preset().is_predefined:

            if imgui.button("Delete"):
                imgui.open_popup("Confirm Deletion")

            # Confirmation popup logic
            if self.confirm_dialog(f'Are you sure you want to delete the preset "{self.current_preset_name}" ?', "Confirm Deletion"):
                self.delete_selected_preset()


    def delete_selected_preset(self):
        """
        Deletes the selected preset from the filesystem and updates the UI.
        """
        assert( self.selected_preset_index != -1, "No preset is selected." )

        full_path = self.get_full_preset_path(self.current_preset_name)

        try:
            presets_manager.delete_preset(full_path)
        except Exception as e:
            logging.error(f"Failed to delete preset: {e}")

        # Update the list of presets to reflect the deletion
        self.update_presets_list()
  

    def presets_open_folder_ui(self, params: PlasmaFractalParams):
        """
        Opens the folder where the user presets are stored.
        """            
        if imgui.button("Open Folder"):

            current_preset = self.get_current_preset()

            # Get current preset's directory path
            directory = self.app_presets_directory if current_preset.is_predefined else self.user_presets_directory
            preset_subdir = os.path.dirname(current_preset.relative_file_path)
            preset_dir = os.path.join(directory, preset_subdir)

            self.open_folder(preset_dir)


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

    def get_current_preset(self) -> Preset:
        """
        Returns the currently selected preset, or None if no preset is selected.
        """
        if self.selected_preset_index >= 0:
            return self.preset_list[self.selected_preset_index]

        return None


    def update_presets_list(self):
        """
        If necessary, this method fetches presets from application-specific and user-specific directories, updating
        the internal list of presets that will show in the UI.
        """
        self.preset_list = presets_manager.list_presets(self.app_presets_directory, self.user_presets_directory)

        self.selected_preset_index = -1  # Reset selection


    def apply_preset(self, params: PlasmaFractalParams, selected_preset: Preset):
        """
        Loads the preset data from a file and updates the current fractal parameters accordingly.

        Args:
            params (PlasmaFractalParams): The fractal parameters to be updated.
            selected_preset (Preset): The preset selected by the user for application.
        """
        try:
            preset_json = presets_manager.load_preset(selected_preset)
            new_params = PlasmaFractalParams.from_json(preset_json)
            
            params.update(new_params)

            self.new_preset_loaded = True

            logging.info("Preset applied successfully.")

        except Exception as e:
            # TODO: Show an error message to the user
            logging.error(f"Error applying preset: {str(e)}")


    def save_preset(self, params: PlasmaFractalParams):
        """
        Saves the current plasma fractal settings as a preset file in the user-specific directory, under the current preset name, 
        overwriting an existing file if necessary.
        """
        try:
            json = params.to_json()
            full_path = self.get_full_preset_path(self.current_preset_name)
                        
            presets_manager.save_preset(full_path, json)

            # Update the list of presets to reflect the new file
            self.update_presets_list()

        except Exception as e:
            # TODO: Show an error message to the user
            logging.error(f"Error saving preset: {str(e)}")


    def get_full_preset_path(self, preset_name: str) -> str:
        """
        Returns the full path to a preset file given its name.
        """
        file_name = preset_name + '.json' if not preset_name.lower().endswith('.json') else preset_name
        return os.path.join(self.user_presets_directory, file_name)


    #.......................... Recording methods ...........................................................................

    def handle_recording_tab(self, params: PlasmaFractalParams):

        imgui.spacing()

        with ih.resized_items(-120):

            # Filename input
            ih.input_text("Filename", self, 'recording_file_name', buffer_size=256)

            # Common video resolutions
            common_resolutions = {
                'HD 720p'      : (1280,  720),
                'Full HD 1080p': (1920, 1080),
                '2K'           : (2560, 1440),
                '4K UHD'       : (3840, 2160)
            }
            resolution_names = list(common_resolutions.keys())

            # Resolution combo box refactored to use list_combo helper
            ih.list_combo("Resolution", self, 'recording_resolution', items=resolution_names)
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
                self.is_recording = not self.is_recording

            # Check to automatically stop the recording if the duration exceeds the set limit
            if self.is_recording and self.recording_time is not None and self.recording_duration > 0:
                if self.recording_time >= self.recording_duration:
                    self.is_recording = False

            # Display recording time if recording
            if self.is_recording and self.recording_time is not None:
                imgui.spacing()
                recording_time_str = self.convert_seconds_to_hms(self.recording_time)
                imgui.text(f"Recording time: {recording_time_str}")

            # Add a button to open the video folder
            if not self.is_recording:
                imgui.spacing()
                if imgui.button("Open Folder"):
                    self.open_folder(self.recording_directory)

    @staticmethod
    def convert_seconds_to_hms(seconds: Union[int, float]) -> str:
        seconds = int(seconds)  # Ensure seconds are whole numbers
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"