from typing import *
from PyPlasmaFractal.mylib.config.serializable_config import SerializableConfig
from PyPlasmaFractal.mylib.config.function_registry import *
from PyPlasmaFractal.mylib.noise.fractal_noise_params import FractalNoiseParams
from PyPlasmaFractal.plasma_fractal_types import ShaderFunctionType


class PlasmaFractalParams(SerializableConfig):
    """
    Represents the parameters for a plasma fractal.
    This class stores various attributes that define the settings for a plasma fractal.
    """
    
    def __init__(self, shader_function_registries: Dict[ShaderFunctionType, FunctionRegistry]):
        super().__init__()
        
        # Initialize private variables (not serialized)
        self._shader_function_registries = shader_function_registries
        self._noise_function_registry = shader_function_registries[ShaderFunctionType.NOISE]
        self._blend_function_registry = shader_function_registries[ShaderFunctionType.BLEND]
        self._warp_function_registry  = shader_function_registries[ShaderFunctionType.WARP]
        self._color_function_registry = shader_function_registries[ShaderFunctionType.COLOR]

        # Initialize general settings
        self.speed = 1.0

        # Initialize basic noise parameters
        self.noise = FractalNoiseParams()
        self.noise.noise_algorithm = self._noise_function_registry.get_function_keys()[0]

        # Initialize warp noise parameters, with some different defaults
        self.warp_noise = FractalNoiseParams()
        self.warp_noise.noise_algorithm = self._noise_function_registry.get_function_keys()[0]
        self.warp_noise.gain = 0.3
        self.warp_noise.time_offset = 42.0   # Use different time offset, to ensure different appearance

        # Output settings for noise
        self.brightness = 1.0
        self.contrast_steepness = 10.0
        self.contrast_midpoint = 0.5
        
        # FEEDBACK
        
        self.enable_feedback = False

        # Feedback blend function settings
        self.feedback_function = self._blend_function_registry.get_function_keys()[0]   # Default to first function
        self.feedback_params = self._blend_function_registry.get_all_param_defaults()
        
        # Feedback blur settings
        self.enable_feedback_blur = False
        self.feedback_blur_radius = 2
        self.feedback_blur_radius_power = 1.0
        
        # Warp settings for feedback
        self.warp_function = self._warp_function_registry.get_function_keys()[0]   # Default to first function
        self.warp_params = self._warp_function_registry.get_all_param_defaults()

        # COLOR
        self.color_function = self._color_function_registry.get_function_keys()[0]  # Default to first function
        self.color_params = self._color_function_registry.get_all_param_defaults()
         
         
    def get_current_feedback_blend_function_info(self) -> FunctionInfo:
        """ Return the current blend function info. """
        return self._blend_function_registry.get_function_info(self.feedback_function)
 
    def get_current_warp_function_info(self) -> FunctionInfo:
        """ Return the current warp function info. """
        return self._warp_function_registry.get_function_info(self.warp_function)

    def get_current_color_function_info(self) -> FunctionInfo:
        """ Return the current color function info. """
        return self._color_function_registry.get_function_info(self.color_function)


    def get_current_feedback_params(self) -> List[Any]:
        """Get ordered parameter values for GLSL function call."""
        return list(self.feedback_params[self.feedback_function].values())
    
    def get_current_warp_params(self) -> List[Any]:
        """Get ordered parameter values for GLSL function call."""
        return list(self.warp_params[self.warp_function].values())
    
    def get_current_color_params(self) -> List[Any]:
        """Get ordered parameter values for GLSL function call."""
        return list(self.color_params[self.color_function].values())


    def apply_defaults(self) -> None:
        """ Reset all attributes to their default values. """
        self.__init__(self._shader_function_registries)
