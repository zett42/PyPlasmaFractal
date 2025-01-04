import datetime
from pathlib import Path
from typing import Union
import imgui

from PyPlasmaFractal.gui.utils.common_controls import confirm_dialog, open_folder_button
from PyPlasmaFractal.gui.utils.common_types import GuiNotification
import PyPlasmaFractal.mylib.gui.imgui_helper as ih
from PyPlasmaFractal.mylib.gui.notification_manager import NotificationManager
from PyPlasmaFractal.plasma_fractal_params import PlasmaFractalParams

class RecordingTab:
    """
    Manages the UI controls for video recording in the plasma fractal visualization.
    """

    def __init__(self, recording_directory: Union[Path, str], default_recording_fps: int, notifications: NotificationManager[GuiNotification]):
        
        self.recording_directory = Path(recording_directory)
        self.notifications = notifications

        self.recording_file_name = f"Capture_{datetime.datetime.now().strftime('%y%m%d_%H%M')}.mp4"
        self.recording_last_saved_file_path = None
        self.recording_resolution = 'HD 720p'
        self.recording_width = None
        self.recording_height = None
        self.recording_fps = default_recording_fps
        self.recording_duration = 30
        self.recording_quality = 8
        self.recording_time = None
        self.recording_error_message = None
        self.is_recording = False
       

    def update(self):
        
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
