from typing import *

from PyPlasmaFractal.mylib.gfx.function_registry import *
from PyPlasmaFractal.mylib.config.json_merge import MergePolicy, handle_type_mismatch_gracefully, json_deep_merge
from PyPlasmaFractal.types import ShaderFunctionType


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
        self.timeScaleFactor = 1.3
        self.positionScaleFactor = 2.0
        self.rotationAngleIncrement = 0.0
        self.timeOffsetIncrement = 12.0
        
        # Output settings for noise
        self.brightness = 1.0
        self.contrastSteepness = 10.0
        self.contrastMidpoint = 0.5
        
        # FEEDBACK
        
        self.enable_feedback = False

        # Feedback blend function settings
        self.feedback_function = self._blend_function_registry.get_function_keys()[0]   # Default to first function
        self.feedback_params = self._blend_function_registry.get_all_param_defaults()
        
        # Warp settings for feedback
        self.warpFunction = self._warp_function_registry.get_function_keys()[0]   # Default to first function
        self.warpParams = self._warp_function_registry.get_all_param_defaults()

        self.warpSpeed = 1.0
        self.warpNoiseAlgorithm = self._noise_function_registry.get_function_keys()[0]   # Default to first function
        self.warpScale = 1.0
        self.warpOctaves = 1
        self.warpGain = 0.3
        self.warpAmplitude = 1.0  # Assuming a default value for amplitude
        self.warpTimeScaleFactor = 1.0
        self.warpPositionScaleFactor = 2.0
        self.warpRotationAngleIncrement = 0.0
        self.warpTimeOffsetInitial = 42.0
        self.warpTimeOffsetIncrement = 12.0
         
         
    def get_current_feedback_function_info(self) -> FunctionInfo:
        """ Return the current blend function info. """
        return self._blend_function_registry.get_function_info(self.feedback_function)

    def get_current_feedback_params(self) -> List[float]:
        """ Return the current feedback parameters. """
        return self.feedback_params[self.feedback_function]
             
    
    def get_current_warp_function_info(self) -> FunctionInfo:
        """ Return the current warp function info. """
        return self._warp_function_registry.get_function_info(self.warpFunction)

    def get_current_warp_params(self) -> List[float]:
        """ Return the current warp parameters. """
        return self.warpParams[self.warpFunction]


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
            setattr(self, key, value)
