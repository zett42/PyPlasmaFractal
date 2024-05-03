from typing import *
import imgui

from mylib.adjust_color import modify_rgba_color_hsv
from plasma_fractal_params import PlasmaFractalParams
import mylib.imgui_helper as ih

# Define the GUI controls for the plasma fractal
def handle_imgui_controls(params: PlasmaFractalParams, ui_state: dict[str, Any]):

    style = imgui.get_style()

    # Adjust header (and item selection) color
    imgui.push_style_color(imgui.COLOR_HEADER, *modify_rgba_color_hsv(style.colors[imgui.COLOR_HEADER], -0.05, 1.0, 1.0))

    width = imgui.get_content_region_available_width()

    imgui.set_next_item_width(width - 160)
    ih.slider_float("Speed", params, 'speed', min_value=0.1, max_value=10.0, flags=imgui.SLIDER_FLAGS_LOGARITHMIC)
    imgui.same_line()
    ih.checkbox("Paused", ui_state, index='animation_paused')
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


# Define the GUI controls for the noise settings
def handle_noise_tab(params: PlasmaFractalParams, ui_state: dict[str, Any]):

    width = imgui.get_content_region_available_width()
    imgui.push_item_width(width - 140) 

    # Noise Settings
    if ih.collapsing_header("Noise Settings", ui_state, index='noise_settings_open'):
        ih.slider_float("Scale", params, 'scale', min_value=0.1, max_value=100.0, flags=imgui.SLIDER_FLAGS_LOGARITHMIC)
        ih.enum_combo("Noise Algorithm", params, 'noise_algorithm')

    # Octave Settings
    if ih.collapsing_header("Fractal Settings", ui_state, index='fractal_settings_open'):
        ih.slider_int("Num. Octaves", params, 'octaves', min_value=1, max_value=12)
        ih.slider_float("Gain", params, 'gain', min_value=0.1, max_value=1.0)
        ih.slider_float("Time Scale", params, 'timeScaleFactor', min_value=0.1, max_value=2.0)
        ih.slider_float("Position Scale", params, 'positionScaleFactor', min_value=0.1, max_value=10.0)
        ih.slider_float("Angle Offset ", params, 'rotationAngleIncrement', min_value=0.0, max_value=0.5)
        ih.slider_float("Time Offset", params, 'timeOffsetIncrement', min_value=0.0, max_value=20.0)

    # Contrast Settings
    if ih.collapsing_header("Output Settings", ui_state, index='output_settings_open'):
        ih.slider_float("Brightness", params, 'brightness', min_value=0.0, max_value=2.0)
        ih.slider_float("Contrast", params, 'contrastSteepness', min_value=0.001, max_value=50.0)
        ih.slider_float("Contrast Midpoint", params, 'contrastMidpoint', min_value=0.0, max_value=1.0)


# Define the GUI controls for the feedback settings
def handle_feedback_tab(params: PlasmaFractalParams, ui_state: dict[str, Any]):

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


# Define the GUI controls for the feedback settings
def handle_feedback_controls(params: PlasmaFractalParams, ui_state: dict[str, Any]):

    width = imgui.get_content_region_available_width()
    imgui.push_item_width(width - 140)    

    # Feedback General Settings
    if ih.collapsing_header("Feedback Mix Settings", ui_state, index='feedback_general_settings_open'):

        ih.slider_float("Feedback Decay", params, 'feedback_decay', min_value=0, max_value=1.0, flags=imgui.SLIDER_FLAGS_LOGARITHMIC)

    # Feedback Noise Settings
    if ih.collapsing_header("Feedback Noise Settings", ui_state, index='feedback_warp_noise_settings_open'):

        ih.slider_float("Speed", params, 'warpSpeed', min_value=0.1, max_value=10.0)
        ih.slider_float("Scale", params, 'warpScale', min_value=0.1, max_value=20.0)
        ih.enum_combo("Noise Algorithm", params, 'warpNoiseAlgorithm')

    # Feedback Octave Settings
    if ih.collapsing_header("Feedback Fractal Settings", ui_state, index='feedback_warp_octave_settings_open'):

        ih.slider_int("Num. Octaves", params, 'warpOctaves', min_value=1, max_value=12)
        ih.slider_float("Gain", params, 'warpGain', min_value=0.1, max_value=1.0)
        ih.slider_float("Time Scale", params, 'warpTimeScaleFactor', min_value=0.1, max_value=2.0)
        ih.slider_float("Position Scale", params, 'warpPositionScaleFactor', min_value=0.1, max_value=10.0)
        ih.slider_float("Rotation", params, 'warpRotationAngleIncrement', min_value=0.0, max_value=0.5)
        ih.slider_float("Time Offset", params, 'warpTimeOffsetIncrement', min_value=0.0, max_value=20.0)

    # Feedback Effect Settings
    if ih.collapsing_header("Feedback Effect Settings", ui_state, index='feedback_warp_effect_settings_open'):

        ih.list_combo("Warp Function", params, 'warpFunction', items=params.get_warp_function_names())

        # Update GUI slider for each parameter in the selected warp function

        warp_params = params.get_current_warp_params()

        for index, paramInfo in enumerate(params.get_current_warp_function_info().params):

            # Define the label with a unique identifier to avoid collisions
            label = f"{paramInfo.displayName}##{params.warpFunction}"

            ih.slider_float(label, warp_params, index=index,
                            min_value=paramInfo.min, max_value=paramInfo.max, 
                            flags=imgui.SLIDER_FLAGS_LOGARITHMIC if paramInfo.logarithmic else 0)


selected_item_index = -1  # Initialize with -1 to indicate no selection
 
def handle_presets_tab(params: PlasmaFractalParams, ui_state: dict[str, Any]):

    global selected_item_index
    preset_names = ["NebulaCore", "LiquidDream", "VortexWaves", "EtherealMist", "ChaosCascade"]

    with imgui.begin_list_box("Available Presets", 250, 200) as list_box:
        if list_box.opened:
            for i, item in enumerate(preset_names):
                _, is_selected = imgui.selectable(item, selected_item_index == i)
                if is_selected and selected_item_index != i:
                    selected_item_index = i
                    print(f"Selected: {item}")
                    