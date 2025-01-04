import datetime
import logging
from pathlib import Path
from typing import *
import imgui
 
from PyPlasmaFractal.gui.utils.common_controls import confirm_dialog, open_folder_button
from PyPlasmaFractal.mylib.config.config_path_manager import ConfigPathManager
from PyPlasmaFractal.mylib.config.json_file_storage import JsonFileStorage
from PyPlasmaFractal.mylib.config.source_manager import StorageSourceManager
from PyPlasmaFractal.mylib.config.function_registry import FunctionRegistry
from PyPlasmaFractal.mylib.gui.notification_manager import NotificationManager
from PyPlasmaFractal.mylib.gui.window_fade_manager import WindowFadeManager
import PyPlasmaFractal.mylib.gui.imgui_helper as ih
from PyPlasmaFractal.mylib.color.adjust_color import modify_rgba_color_hsv
from PyPlasmaFractal.plasma_fractal_types import ShaderFunctionType
from .plasma_fractal_params import PlasmaFractalParams
from PyPlasmaFractal.gui.utils.common_types import GuiNotification
from PyPlasmaFractal.gui.tabs.noise_tab import NoiseTab
from PyPlasmaFractal.gui.tabs.feedback_tab import FeedbackTab
from PyPlasmaFractal.gui.tabs.color_tab import ColorTab
from PyPlasmaFractal.gui.tabs.presets_tab import PresetTab

class PlasmaFractalGUI:
    """
    Manages the user interface for PyPlasmaFractal.
      
    Attributes:
        preset_list (List[Preset]): A list of available presets, populated on-demand.
        selected_preset_index (int): The index of the currently selected preset in the list.
        animation_paused (bool): Flag to indicate whether the animation is paused.
        noise_settings_open (bool): Flag to control the visibility of the noise settings.
        fractal_settings_open (bool): Flag to control the visibility of fractal settings.
        basic_color_settings_open (bool): Flag to control the visibility of output settings.
        feedback_general_settings_open (bool): Flag to control the visibility of general feedback settings.
        feedback_warp_noise_settings_open (bool): Flag to control the visibility of feedback noise settings.
        feedback_warp_octave_settings_open (bool): Flag to control the visibility of feedback octave settings.
        feedback_warp_effect_settings_open (bool): Flag to control the visibility of feedback effect settings.
    """

    # Notification types for the notification manager

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
        self.basic_color_settings_open = True
        self.feedback_general_settings_open = True
        self.feedback_blur_settings_open = True
        self.feedback_warp_noise_settings_open = True
        self.feedback_warp_effect_settings_open = True
        self.feedback_color_adjustment_open = True
        self.color_function_settings_open = True

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
        self.notifications = NotificationManager[GuiNotification]()

        # Initialize tab objects
        self.noise_tab = NoiseTab(self.noise_function_registry)
        self.feedback_tab = FeedbackTab(self.blend_function_registry, self.warp_function_registry, self.noise_function_registry)
        self.color_tab = ColorTab(self.color_function_registry)
        self.preset_tab = PresetTab(path_manager, self.notifications)

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
                                self.noise_tab.draw(params)

                        with imgui.begin_tab_item("Feedback") as feedback_tab:
                            if feedback_tab.selected:
                                self.feedback_tab.draw(params)

                        with imgui.begin_tab_item("Color") as color_tab:
                            if color_tab.selected:
                                self.color_tab.draw(params)

                        with imgui.begin_tab_item("Presets") as presets_tab:
                            if presets_tab.selected:
                                self.preset_tab.draw(params)

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

        if confirm_dialog("Are you sure you want to reset all settings to their defaults?", confirm_dialog_title):
            params.apply_defaults()
            self.notifications.push_notification(GuiNotification.NEW_PRESET_LOADED)
    
    
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
            if (message := self.notifications.pull_notification(GuiNotification.RECORDING_ERROR)) is not None:
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
                    open_folder_button(self.recording_directory)
                        
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

        if confirm_dialog(f'A recording with this name already exists:\n"{self.recording_file_name}"\n\nDo you want to overwrite it?',
                          dialog_title):
            self.start_recording()                  

    def start_recording(self):

        self.is_recording = True
        self.recording_error_message = None
        self.recording_last_saved_file_path = None
        self.notifications.push_notification(GuiNotification.RECORDING_STATE_CHANGED, {'is_recording': self.is_recording})

    def stop_recording(self):

        self.is_recording = False
        self.recording_last_saved_file_path = self.recording_directory / self.recording_file_name
        self.notifications.push_notification(GuiNotification.RECORDING_STATE_CHANGED, {'is_recording': self.is_recording})

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

