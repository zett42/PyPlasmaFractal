import imgui
import PyPlasmaFractal.mylib.gui.imgui_helper as ih
from PyPlasmaFractal.plasma_fractal_params import PlasmaFractalParams
from PyPlasmaFractal.mylib.config.function_registry import FunctionRegistry
from PyPlasmaFractal.gui.utils.common_controls import function_settings
from PyPlasmaFractal.mylib.color.adjust_color import sigmoid_contrast


class ColorTab:
    """
    Manages the UI controls for adjusting color-related settings in the plasma fractal visualization.
    """

    def __init__(self, color_function_registry: FunctionRegistry):
        
        self.color_function_registry = color_function_registry
        
        self.basic_settings_open = True
        self.color_function_settings_open = True
        self.feedback_color_settings_open = True

    def draw(self, params: PlasmaFractalParams):
        
        with ih.resized_items(-160):
            if ih.collapsing_header("Basic Settings", self, attr='basic_settings_open'):
                
                ih.slider_float("Brightness", params, 'brightness', min_value=0.0, max_value=2.0)
                ih.show_tooltip("Adjust the brightness of the grayscale noise, before any colorization is applied.\n"
                              "Higher values increase the overall intensity of the noise pattern.")
                
                ih.slider_float("Contrast", params, 'contrast_steepness', min_value=0.001, max_value=50.0)
                ih.show_tooltip("Set the contrast steepness of the grayscale noise, before any colorization is applied.\n"
                              "Higher values result in sharper contrasts between light and dark areas.")
                
                ih.slider_float("Contrast Midpoint", params, 'contrast_midpoint', min_value=0.0, max_value=1.0)
                ih.show_tooltip("Adjust the contrast midpoint of the grayscale noise, before any colorization is applied.\n"
                              "Higher values shift the midpoint towards the brighter end of the intensity range.")

                ih.plot_callable('##output_curve', 
                               lambda x: sigmoid_contrast(x, params.contrast_steepness, params.contrast_midpoint) * params.brightness, 
                               scale_max=2.0)

            function_settings(self, header="Colorization Settings", header_attr='color_function_settings_open', 
                              registry=self.color_function_registry, function_attr='color_function', 
                              params_attr='color_params', params=params)

            if params.enable_feedback:
                
                if ih.collapsing_header("Feedback Color Settings", self, attr='feedback_color_settings_open'): 
                                       
                    ih.checkbox("Enable Color Adjustment", params, 'enable_feedback_color_adjust')   
                                     
                    if params.enable_feedback_color_adjust:
                        ih.slider_float("Hue Shift", params, 'feedback_hue_shift', 
                                      min_value=-1.0, max_value=1.0, flags=imgui.SLIDER_FLAGS_LOGARITHMIC)
                        ih.show_tooltip("Shift the hue of the feedback frame, which causes the hue to gradually change over time.")
                        
                        ih.slider_float("Saturation Adjust", params, 'feedback_saturation', 
                                      min_value=-1.0, max_value=1.0, flags=imgui.SLIDER_FLAGS_LOGARITHMIC)
                        ih.show_tooltip("Adjust the saturation of the feedback frame, which causes the saturation to gradually change over time.")
