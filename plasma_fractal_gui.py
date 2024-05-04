import logging
import os
from typing import *
import imgui
from dataclasses import dataclass, field

from mylib.config_file_manager import ConfigFileManager
from plasma_fractal_params import PlasmaFractalParams
import mylib.imgui_helper as ih
from mylib.adjust_color import modify_rgba_color_hsv
from mylib.presets_manager import Preset, list_presets, load_preset

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
    def __init__(self):

        self.preset_list = []
        self.selected_preset_index = -1
        self.animation_paused = False
        self.noise_settings_open = True
        self.fractal_settings_open = True
        self.output_settings_open = True
        self.feedback_general_settings_open = True
        self.feedback_warp_noise_settings_open = True
        self.feedback_warp_octave_settings_open = True
        self.feedback_warp_effect_settings_open = True

    
    def update(self, params: PlasmaFractalParams):
        """
        Updates the UI elements in the control panel for managing plasma fractal visualization settings.

        This method handles the layout and interaction logic for the control panel, organizing settings into
        tabs. It allows users to modify plasma fractal parameters directly through graphical controls like sliders and checkboxes.

        Args:
            params (PlasmaFractalParams): The current settings of the plasma fractal that can be adjusted via the UI.
        """
        imgui.begin("Control Panel")

        style = imgui.get_style()
        imgui.push_style_color(imgui.COLOR_HEADER, *modify_rgba_color_hsv(style.colors[imgui.COLOR_HEADER], -0.05, 1.0, 1.0))

        width = imgui.get_content_region_available_width()

        imgui.set_next_item_width(width - 160)
        ih.slider_float("Speed", params, 'speed', min_value=0.1, max_value=10.0, flags=imgui.SLIDER_FLAGS_LOGARITHMIC)

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

        imgui.pop_style_color(1)
        imgui.end()
    

    def handle_noise_tab(self, params: PlasmaFractalParams):
        """
        Manages the UI controls for adjusting noise-related settings in the plasma fractal visualization.

        Args:
            params (PlasmaFractalParams): The current settings of the plasma fractal that can be adjusted via the UI.
        """
        width = imgui.get_content_region_available_width()
        imgui.push_item_width(width - 140)

        if ih.collapsing_header("Noise Settings", self, attr='noise_settings_open'):
            ih.slider_float("Scale", params, 'scale', min_value=0.1, max_value=100.0, flags=imgui.SLIDER_FLAGS_LOGARITHMIC)
            ih.enum_combo("Noise Algorithm", params, 'noise_algorithm')

        if ih.collapsing_header("Fractal Settings", self, attr='fractal_settings_open'):
            ih.slider_int("Num. Octaves", params, 'octaves', min_value=1, max_value=12)
            ih.slider_float("Gain", params, 'gain', min_value=0.1, max_value=1.0)
            ih.slider_float("Time Scale", params, 'timeScaleFactor', min_value=0.1, max_value=2.0)
            ih.slider_float("Position Scale", params, 'positionScaleFactor', min_value=0.1, max_value=10.0)
            ih.slider_float("Angle Offset", params, 'rotationAngleIncrement', min_value=0.0, max_value=0.5)
            ih.slider_float("Time Offset", params, 'timeOffsetIncrement', min_value=0.0, max_value=20.0)

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
        width = imgui.get_content_region_available_width()
        imgui.push_item_width(width - 140)

        if ih.collapsing_header("Feedback Mix Settings", self, attr='feedback_general_settings_open'):
            ih.slider_float("Feedback Decay", params, 'feedback_decay', min_value=0, max_value=1.0, flags=imgui.SLIDER_FLAGS_LOGARITHMIC)

        if ih.collapsing_header("Feedback Noise Settings", self, attr='feedback_warp_noise_settings_open'):
            ih.slider_float("Speed", params, 'warpSpeed', min_value=0.1, max_value=10.0)
            ih.slider_float("Scale", params, 'warpScale', min_value=0.1, max_value=20.0)
            ih.enum_combo("Noise Algorithm", params, 'warpNoiseAlgorithm')

        if ih.collapsing_header("Feedback Fractal Settings", self, attr='feedback_warp_octave_settings_open'):
            ih.slider_int("Num. Octaves", params, 'warpOctaves', min_value=1, max_value=12)
            ih.slider_float("Gain", params, 'warpGain', min_value=0.1, max_value=1.0)
            ih.slider_float("Time Scale", params, 'warpTimeScaleFactor', min_value=0.1, max_value=2.0)
            ih.slider_float("Position Scale", params, 'warpPositionScaleFactor', min_value=0.1, max_value=10.0)
            ih.slider_float("Rotation", params, 'warpRotationAngleIncrement', min_value=0.0, max_value=0.5)
            ih.slider_float("Time Offset", params, 'warpTimeOffsetIncrement', min_value=0.0, max_value=20.0)

        if ih.collapsing_header("Feedback Effect Settings", self, attr='feedback_warp_effect_settings_open'):
            ih.list_combo("Warp Function", params, 'warpFunction', items=params.get_warp_function_names())

            for index, paramInfo in enumerate(params.get_current_warp_function_info().params):

                label = f"{paramInfo.displayName}##{params.warpFunction}"
                ih.slider_float(label, params.get_current_warp_params(), index=index,
                                min_value=paramInfo.min, max_value=paramInfo.max, 
                                flags=imgui.SLIDER_FLAGS_LOGARITHMIC if paramInfo.logarithmic else 0)


    def handle_presets_tab(self, params: PlasmaFractalParams):
        """
        Manages the presets tab in the UI, allowing users to load and apply presets for plasma fractal configurations.

        Args:
            params (PlasmaFractalParams): The fractal parameters that can be modified by applying a preset.
        """
        width = imgui.get_content_region_available_width()

        if not self.preset_list:
            self.load_presets()

        # Insert a label manually above the listbox as by default label puts the text on the right side, which wastes space
        imgui.spacing()
        imgui.text("Available Presets:")
        imgui.spacing()

        # Label is just an ID, because we already added a label manually above
        if imgui.begin_list_box("##AvailablePresets", width, 200):
            for i, preset in enumerate(self.preset_list):

                display_name = f"* {preset.relative_file_path}" if preset.is_predefined else preset.relative_file_path
                _, is_selected = imgui.selectable(display_name, self.selected_preset_index == i)

                if is_selected and self.selected_preset_index != i:
                    self.selected_preset_index = i

            imgui.end_list_box()

        if imgui.button("Load Preset"):
            if self.selected_preset_index != -1:
                selected_preset = self.preset_list[self.selected_preset_index]
                self.apply_preset(params, selected_preset)


    def load_presets(self):
        """
        This method fetches presets from application-specific and user-specific directories, updating
        the internal list of presets. It ensures that the presets are refreshed and available for user interaction
        in the presets tab.
        """
        app_presets_path, user_presets_path = self.get_preset_paths()
        self.preset_list = list_presets(app_presets_path, user_presets_path)


    def get_preset_paths(self):
        """
        Retrieves the file system paths for loading presets.

        Returns:
            tuple: A tuple containing the path for application presets and user presets.
        """
        presets_sub_dir = 'presets'
        
        script_dir = os.path.dirname(os.path.realpath(__file__))
        app_presets_path = os.path.join(script_dir, presets_sub_dir)
        
        # TODO: Instead of adding a dependency to ConfigFileManager for this, we 
        #       we should factor out the directory logic from ConfigFileManager into a separate function.
        user_presets_path = ConfigFileManager('PlasmaFractal', 'zett42', sub_dir=presets_sub_dir, use_user_dir=True).directory
        
        return app_presets_path, user_presets_path


    def apply_preset(self, params: PlasmaFractalParams, selected_preset: Preset):
        """
        Loads the preset data from a file and updates the current fractal parameters accordingly.

        Args:
            params (PlasmaFractalParams): The fractal parameters to be updated.
            selected_preset (Preset): The preset selected by the user for application.
        """
        try:
            preset_json = load_preset(selected_preset)
            new_params = PlasmaFractalParams.from_json(preset_json)
            params.update(new_params)
            logging.info("Preset applied successfully.")

        except Exception as e:
            # TODO: Show an error message to the user
            logging.error(f"Error applying preset: {str(e)}")