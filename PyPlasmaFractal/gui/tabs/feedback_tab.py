import imgui
import PyPlasmaFractal.mylib.gui.imgui_helper as ih
from PyPlasmaFractal.plasma_fractal_params import PlasmaFractalParams
from PyPlasmaFractal.mylib.config.function_registry import FunctionRegistry
from PyPlasmaFractal.gui.utils.common_controls import function_settings, noise_controls

class FeedbackTab:
    def __init__(self, blend_registry: FunctionRegistry, warp_registry: FunctionRegistry, noise_registry: FunctionRegistry):
        self.blend_function_registry = blend_registry
        self.warp_function_registry = warp_registry
        self.noise_function_registry = noise_registry
        
        self.general_settings_open = True
        self.blur_settings_open = True
        self.warp_noise_settings_open = True
        self.warp_effect_settings_open = True

    def draw(self, params: PlasmaFractalParams):
        """
        Manages the UI controls for the feedback settings in the plasma fractal visualization.

        Args:
            params (PlasmaFractalParams): The current settings of the plasma fractal.
        """
        ih.checkbox("Enable Feedback", params, 'enable_feedback')

        if params.enable_feedback:
            imgui.spacing()
            with ih.resized_items(-160):
                function_settings(self, header="Feedback Mix Settings", header_attr='general_settings_open', 
                                registry=self.blend_function_registry, function_attr='feedback_function', 
                                params_attr='feedback_params', params=params)

                if ih.collapsing_header("Feedback Blur Settings", self, attr='blur_settings_open'):
                    ih.checkbox("Enable Blur", params, 'enable_feedback_blur')
                    if params.enable_feedback_blur:
                        ih.slider_int("Blur Radius", params, 'feedback_blur_radius', min_value=1, max_value=16)
                        ih.slider_float("Blur Radius Power", params, 'feedback_blur_radius_power', 
                                      min_value=0.01, max_value=20, flags=imgui.SLIDER_FLAGS_LOGARITHMIC)
        
                if ih.collapsing_header("Warp Noise Settings", self, attr='warp_noise_settings_open'):
                    noise_controls(params.warp_noise, 'warp_noise', self.noise_function_registry)

                function_settings(self, header="Warp Function Settings", header_attr='warp_effect_settings_open', 
                                registry=self.warp_function_registry, function_attr='warp_function', 
                                params_attr='warp_params', params=params)
            return

        # Display a note when feedback is disabled                
        imgui.spacing()
        imgui.spacing()
        imgui.text_colored("Note", 1.0, 0.9, 0.2)
        imgui.separator()
        imgui.text_wrapped("After enabling feedback, you might want to adjust the contrast on the \"Color\" tab for better results.")
