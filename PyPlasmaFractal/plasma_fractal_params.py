from typing import *

from PyPlasmaFractal.mylib.config.function_registry import *
from PyPlasmaFractal.mylib.config.json_merge import MergePolicy, handle_type_mismatch_gracefully, json_deep_merge
from PyPlasmaFractal.plasma_fractal_types import ShaderFunctionType


class PlasmaFractalParams:
    """
    Represents the parameters for a plasma fractal.
    This class stores various attributes that define the settings for a plasma fractal.
    """
    
    def __init__(self, shader_function_registries: Dict[ShaderFunctionType, FunctionRegistry]):
        """
        Initializes a new instance of the PlasmaFractalParams class with default values.
        """ 

        # Initialize private variables (not serialized)
        self._shader_function_registries = shader_function_registries
        self._noise_function_registry = shader_function_registries[ShaderFunctionType.NOISE]
        self._blend_function_registry = shader_function_registries[ShaderFunctionType.BLEND]
        self._warp_function_registry  = shader_function_registries[ShaderFunctionType.WARP]

        # NOISE
        
        # General noise settings
        self.speed = 1.0
        self.scale = 2.0
        
        # Specific noise settings
        self.noise_algorithm = self._noise_function_registry.get_function_keys()[0]   # Default to first function
        self.octaves = 1
        self.gain = 0.5
        self.time_scale_factor = 1.3
        self.position_scale_factor = 2.0
        self.rotation_angle_increment = 0.0
        self.time_offset_increment = 12.0
        
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

        self.warp_speed = 1.0
        self.warp_noise_algorithm = self._noise_function_registry.get_function_keys()[0]   # Default to first function
        self.warp_scale = 1.0
        self.warp_octaves = 1
        self.warp_gain = 0.3
        self.warp_amplitude = 1.0  # Assuming a default value for amplitude
        self.warp_time_scale_factor = 1.0
        self.warp_position_scale_factor = 2.0
        self.warp_rotation_angle_increment = 0.0
        self.warp_time_offset_initial = 42.0
        self.warp_time_offset_increment = 12.0
         
         
    def get_current_feedback_blend_function_info(self) -> FunctionInfo:
        """ Return the current blend function info. """
        return self._blend_function_registry.get_function_info(self.feedback_function)

    def get_current_feedback_params(self) -> List[Any]:
        """ Return the current feedback parameters. """
        return self.feedback_params[self.feedback_function]
             
    
    def get_current_warp_function_info(self) -> FunctionInfo:
        """ Return the current warp function info. """
        return self._warp_function_registry.get_function_info(self.warp_function)

    def get_current_warp_params(self) -> List[Any]:
        """ Return the current warp parameters. """
        return self.warp_params[self.warp_function]


    def apply_defaults(self) -> None:
        """ Reset all attributes to their default values. """
        self.__init__(self._shader_function_registries)
    
    
    #............ Serialization helpers ........................................................................

    def to_dict(self) -> dict:
        """
        Convert the public attributes to a dictionary.

        Returns:
        dict: A dictionary representation of the instance.
        """
        return {key: value for key, value in self.__dict__.items() if not key.startswith('_')}
             
    def merge_dict(self, source: dict) -> None:
        """
        Update the instance with the values from a dictionary.
        Only sets attributes from the dictionary that already exist in the instance.
        Handles type mismatches gracefully to avoid data migration issues.
        """
        merged = json_deep_merge(self.to_dict(), source, default_merge_policy=MergePolicy.MERGE_EXISTING, 
                                 handle_type_mismatch=handle_type_mismatch_gracefully)
        
        for key, value in merged.items():
            if not key.startswith('_'):
                setattr(self, key, value)
