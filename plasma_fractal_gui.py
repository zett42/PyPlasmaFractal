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
# The UIState class is used to store the state of the GUI controls that are not directly related to PlasmaFractalParams.

@dataclass
class UIState:
    preset_list: List[Preset] = field(default_factory=list)  # Ensure each instance has its own unique list to prevent shared state across instances.
    selected_preset_index: int = -1
    animation_paused: bool = False
    noise_settings_open: bool = True
    fractal_settings_open: bool = True
    output_settings_open: bool = True
    feedback_general_settings_open: bool = True
    feedback_warp_noise_settings_open: bool = True
    feedback_warp_octave_settings_open: bool = True
    feedback_warp_effect_settings_open: bool = True

#------------------------------------------------------------------------------------------------------------------------------------
# Define the GUI controls for the plasma fractal

def handle_imgui_controls(params: PlasmaFractalParams, ui_state: UIState):

    style = imgui.get_style()

    # Adjust header (and item selection) color
    imgui.push_style_color(imgui.COLOR_HEADER, *modify_rgba_color_hsv(style.colors[imgui.COLOR_HEADER], -0.05, 1.0, 1.0))

    width = imgui.get_content_region_available_width()

    imgui.set_next_item_width(width - 160)
    ih.slider_float("Speed", params, 'speed', min_value=0.1, max_value=10.0, flags=imgui.SLIDER_FLAGS_LOGARITHMIC)
    imgui.same_line()
    ih.checkbox("Paused", ui_state, attr='animation_paused')
    imgui.spacing()

    with imgui.begin_tab_bar("Control Tabs") as tab_bar:
        if tab_bar.opened:

            with imgui.begin_tab_item("Noise") as noise_tab:
                if noise_tab.selected:
                    handle_noise_tab(params, ui_state)

            with imgui.begin_tab_item("Feedback") as feedback_tab:
                if feedback_tab.selected:
                    handle_feedback_tab(params, ui_state)

            with imgui.begin_tab_item("Presets") as presets_tab:
                 if presets_tab.selected:
                     handle_presets_tab(params, ui_state)

    # Revert to the original color
    imgui.pop_style_color(1)


#------------------------------------------------------------------------------------------------------------------------------------
# Define the GUI controls for the noise settings

def handle_noise_tab(params: PlasmaFractalParams, ui_state: UIState):

    width = imgui.get_content_region_available_width()
    imgui.push_item_width(width - 140) 

    # Noise Settings
    if ih.collapsing_header("Noise Settings", ui_state, attr='noise_settings_open'):
        ih.slider_float("Scale", params, 'scale', min_value=0.1, max_value=100.0, flags=imgui.SLIDER_FLAGS_LOGARITHMIC)
        ih.enum_combo("Noise Algorithm", params, 'noise_algorithm')

    # Octave Settings
    if ih.collapsing_header("Fractal Settings", ui_state, attr='fractal_settings_open'):
        ih.slider_int("Num. Octaves", params, 'octaves', min_value=1, max_value=12)
        ih.slider_float("Gain", params, 'gain', min_value=0.1, max_value=1.0)
        ih.slider_float("Time Scale", params, 'timeScaleFactor', min_value=0.1, max_value=2.0)
        ih.slider_float("Position Scale", params, 'positionScaleFactor', min_value=0.1, max_value=10.0)
        ih.slider_float("Angle Offset ", params, 'rotationAngleIncrement', min_value=0.0, max_value=0.5)
        ih.slider_float("Time Offset", params, 'timeOffsetIncrement', min_value=0.0, max_value=20.0)

    # Contrast Settings
    if ih.collapsing_header("Output Settings", ui_state, attr='output_settings_open'):
        ih.slider_float("Brightness", params, 'brightness', min_value=0.0, max_value=2.0)
        ih.slider_float("Contrast", params, 'contrastSteepness', min_value=0.001, max_value=50.0)
        ih.slider_float("Contrast Midpoint", params, 'contrastMidpoint', min_value=0.0, max_value=1.0)

#------------------------------------------------------------------------------------------------------------------------------------
# Define the GUI controls for the feedback settings

def handle_feedback_tab(params: PlasmaFractalParams, ui_state: UIState):

    ih.checkbox("Enable Feedback", params, 'enable_feedback')

    if params.enable_feedback:
        imgui.spacing()
        handle_feedback_controls(params, ui_state)
    else:
        imgui.spacing()
        imgui.spacing()
        imgui.text_colored("Note", 1.0, 0.9, 0.2)
        imgui.separator()
        imgui.text_wrapped("After enabling feedback, you might want to adjust the noise settings, particularly the contrast for better results.")

#------------------------------------------------------------------------------------------------------------------------------------
# Define the GUI controls for the feedback settings

def handle_feedback_controls(params: PlasmaFractalParams, ui_state: UIState):

    width = imgui.get_content_region_available_width()
    imgui.push_item_width(width - 140)    

    # Feedback General Settings
    if ih.collapsing_header("Feedback Mix Settings", ui_state, attr='feedback_general_settings_open'):

        ih.slider_float("Feedback Decay", params, 'feedback_decay', min_value=0, max_value=1.0, flags=imgui.SLIDER_FLAGS_LOGARITHMIC)

    # Feedback Noise Settings
    if ih.collapsing_header("Feedback Noise Settings", ui_state, attr='feedback_warp_noise_settings_open'):

        ih.slider_float("Speed", params, 'warpSpeed', min_value=0.1, max_value=10.0)
        ih.slider_float("Scale", params, 'warpScale', min_value=0.1, max_value=20.0)
        ih.enum_combo("Noise Algorithm", params, 'warpNoiseAlgorithm')

    # Feedback Octave Settings
    if ih.collapsing_header("Feedback Fractal Settings", ui_state, attr='feedback_warp_octave_settings_open'):

        ih.slider_int("Num. Octaves", params, 'warpOctaves', min_value=1, max_value=12)
        ih.slider_float("Gain", params, 'warpGain', min_value=0.1, max_value=1.0)
        ih.slider_float("Time Scale", params, 'warpTimeScaleFactor', min_value=0.1, max_value=2.0)
        ih.slider_float("Position Scale", params, 'warpPositionScaleFactor', min_value=0.1, max_value=10.0)
        ih.slider_float("Rotation", params, 'warpRotationAngleIncrement', min_value=0.0, max_value=0.5)
        ih.slider_float("Time Offset", params, 'warpTimeOffsetIncrement', min_value=0.0, max_value=20.0)

    # Feedback Effect Settings
    if ih.collapsing_header("Feedback Effect Settings", ui_state, attr='feedback_warp_effect_settings_open'):

        ih.list_combo("Warp Function", params, 'warpFunction', items=params.get_warp_function_names())

        # Update GUI slider for each parameter in the selected warp function

        warp_params = params.get_current_warp_params()

        for index, paramInfo in enumerate(params.get_current_warp_function_info().params):

            # Define the label with a unique identifier to avoid collisions
            label = f"{paramInfo.displayName}##{params.warpFunction}"

            ih.slider_float(label, warp_params, index=index,
                            min_value=paramInfo.min, max_value=paramInfo.max, 
                            flags=imgui.SLIDER_FLAGS_LOGARITHMIC if paramInfo.logarithmic else 0)

#------------------------------------------------------------------------------------------------------------------------------------
# Define the GUI controls for the presets tab

def handle_presets_tab(params: PlasmaFractalParams, ui_state: UIState):

    width = imgui.get_content_region_available_width()

    if not ui_state.preset_list:
        load_presets(ui_state)
    
    # Manually render the label above the list box, instead of the default right position
    imgui.spacing()
    imgui.text("Available Presets:")
    imgui.spacing()

    # UI display logic for presets list
    # The label is just an ID with no visual label, as we already have a visible label above the list.
    if imgui.begin_list_box("##Available Presets", width, 200):

        for i, preset in enumerate(ui_state.preset_list):

            display_name = f"* {preset.relative_file_path}" if preset.is_predefined else preset.relative_file_path
            _, is_selected = imgui.selectable(display_name, ui_state.selected_preset_index == i)
            if is_selected and ui_state.selected_preset_index != i:
                ui_state.selected_preset_index = i

        imgui.end_list_box()


    if imgui.button("Load Preset"):

        if ui_state.selected_preset_index != -1:
            selected_preset = ui_state.preset_list[ui_state.selected_preset_index]
            apply_preset(params, selected_preset)

#------------------------------------------------------------------------------------------------------------------------------------

def apply_preset(params: PlasmaFractalParams, selected_preset: Preset):
    """
    Load and apply a preset using the PlasmaFractalParams model.

    Args:
    selected_preset (Preset): The preset to load and apply.
    """

    logging.info(f"Loading preset: {selected_preset.relative_file_path}, Predefined: {selected_preset.is_predefined}")

    try:
        # Load the preset data
        preset_json = load_preset(selected_preset)
        
        # Deserialize and apply the preset data
        new_params = PlasmaFractalParams.from_json(preset_json)

        # Update the current parameters with the new values        
        params.update(new_params)

        logging.info("Preset applied successfully.")
        
    except Exception as e:
        # Handle errors related to file operations or JSON parsing
        # TODO: Show an error message to the user
        logging.error(f"Error applying preset: {str(e)}")


#------------------------------------------------------------------------------------------------------------------------------------

def load_presets(ui_state: UIState):

    app_presets_path, user_presets_path = get_preset_paths()

    logging.debug(f"App presets path: {app_presets_path}")
    logging.debug(f"User presets path: {user_presets_path}")

    ui_state.preset_list = list_presets(app_presets_path, user_presets_path)

#------------------------------------------------------------------------------------------------------------------------------------
# Helper functions

def get_preset_paths():
    """
    Determines the paths for the application and user-specific preset directories.

    Returns:
    tuple: A tuple containing the application presets path and user presets path.
    """
    presets_sub_dir = 'presets'
    script_dir = os.path.dirname(os.path.realpath(__file__))
    app_presets_path = os.path.join(script_dir, presets_sub_dir)
    
    # TODO: Don't add a dependency to ConfigFileManager for this. 
    #       We should factor out the directory logic from ConfigFileManager into a separate function.
    user_presets_path = ConfigFileManager('PlasmaFractal', 'zett42', sub_dir=presets_sub_dir, use_user_dir=True).directory

    return (app_presets_path, user_presets_path)
