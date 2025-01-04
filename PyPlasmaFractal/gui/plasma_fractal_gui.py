from pathlib import Path
from typing import *
import imgui
 
from PyPlasmaFractal.gui.common.common_controls import confirm_dialog
from PyPlasmaFractal.mylib.config.config_path_manager import ConfigPathManager
from PyPlasmaFractal.mylib.config.function_registry import FunctionRegistry
from PyPlasmaFractal.mylib.gui.notification_manager import NotificationManager
from PyPlasmaFractal.mylib.gui.window_fade_manager import WindowFadeManager
import PyPlasmaFractal.mylib.gui.imgui_helper as ih
from PyPlasmaFractal.mylib.color.adjust_color import modify_rgba_color_hsv
from PyPlasmaFractal.plasma_fractal_types import ShaderFunctionType
from ..plasma_fractal_params import PlasmaFractalParams
from PyPlasmaFractal.gui.common.common_types import GuiNotification
from PyPlasmaFractal.gui.tabs.noise_tab import NoiseTab
from PyPlasmaFractal.gui.tabs.feedback_tab import FeedbackTab
from PyPlasmaFractal.gui.tabs.color_tab import ColorTab
from PyPlasmaFractal.gui.tabs.presets_tab import PresetTab
from PyPlasmaFractal.gui.tabs.recording_tab import RecordingTab

class PlasmaFractalGUI:
    """
    Manages the user interface for PyPlasmaFractal.
      
    Attributes:
        animation_paused (bool): Indicates whether the plasma fractal animation is paused.
        actual_fps (float): The actual frames per second achieved by the plasma fractal visualization.
        desired_fps (float): The desired frames per second for the plasma fractal visualization.
        fade_manager (WindowFadeManager): Manages the fade effect for the control panel.
        notifications (NotificationManager[GuiNotification]): Manages notifications for the control panel.
    """

    # Notification types for the notification manager

    def __init__(self, path_manager: ConfigPathManager, 
                 function_registries: Dict[ShaderFunctionType, FunctionRegistry],
                 recording_directory: Union[Path, str], 
                 default_recording_fps: int):
         
        self.animation_paused = False
        
        # FPS display
        self.actual_fps = 0.0
        self.desired_fps = 0.0

        # Initialize the fade manager for the control panel
        self.fade_manager = WindowFadeManager()

        # Initialize the notification manager
        self.notifications = NotificationManager[GuiNotification]()

        # Initialize tab objects
        
        noise_function_registry = function_registries[ShaderFunctionType.NOISE]
        blend_function_registry = function_registries[ShaderFunctionType.BLEND]
        warp_function_registry  = function_registries[ShaderFunctionType.WARP]
        color_function_registry = function_registries[ShaderFunctionType.COLOR]       
        
        self.noise_tab = NoiseTab(noise_function_registry)
        self.feedback_tab = FeedbackTab(blend_function_registry, warp_function_registry, noise_function_registry)
        self.color_tab = ColorTab(color_function_registry)
        self.preset_tab = PresetTab(path_manager, self.notifications)
        self.recording_tab = RecordingTab(recording_directory, default_recording_fps, self.notifications)


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

                self.update_main_controls(params)

                with imgui.begin_tab_bar("Control Tabs") as tab_bar:
                    if tab_bar.opened:
                        with imgui.begin_tab_item("Noise") as noise_tab:
                            if noise_tab.selected:
                                self.noise_tab.update(params)

                        with imgui.begin_tab_item("Feedback") as feedback_tab:
                            if feedback_tab.selected:
                                self.feedback_tab.update(params)

                        with imgui.begin_tab_item("Color") as color_tab:
                            if color_tab.selected:
                                self.color_tab.update(params)

                        with imgui.begin_tab_item("Presets") as presets_tab:
                            if presets_tab.selected:
                                self.preset_tab.update(params)

                        with imgui.begin_tab_item("Recording") as recording_tab:
                            if recording_tab.selected:
                                self.recording_tab.update()


    def update_main_controls(self, params: PlasmaFractalParams):
        """
        Draws the main controls that appear above the tabs.
        
        Args:
            params (PlasmaFractalParams): The current settings of the plasma fractal.
        """
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
