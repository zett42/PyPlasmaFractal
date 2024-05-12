from json import JSONEncoder
import json
import logging
from typing import *
from enum import Enum, auto

from mylib.function_registry import *
from mylib.json_helper import convert_json_scalar, type_safe_json_merge


class NoiseAlgorithm(Enum):
    """
    Enumeration of noise algorithms.
    """
    Perlin3D = auto()
    SimplexPerlin3D = auto()


class FractalNoiseVariant(Enum):
    """
    Enumeration of fractal noise variants.
    """
    Single = auto()
    Double = auto()
    Deriv = auto()


class BlendFunction(Enum):
    """
    Enumeration of feedback blend modes.
    """
    Linear = auto()
    Additive = auto()
    Sigmoid = auto()
    
    
class WarpFunction(Enum):
    Offset = auto()
    Polar = auto()
    Swirl = auto()
    SwirlSigmoid = auto()
    SwirlSigmoidDistorted = auto()
    OffsetDeriv = auto()
    InfiniteMirror = auto()
    Test = auto()  
    
    
# Right now we don't need a custom class for BlendFunctionInfo, so just define an alias for consistency.
BlendFunctionInfo = FunctionInfo    
    
class BlendFunctionRegistry(FunctionRegistry):
    """
    A class that statically stores information about feedback blend functions.
    """
    functions = {
        BlendFunction.Linear: BlendFunctionInfo(
            display_name="Linear",
            params=[
                FunctionParam("Feedback Decay", logarithmic=False, min=0.0, max=0.3, default=0.01)
            ]
        ),
        BlendFunction.Additive: BlendFunctionInfo(
            display_name="Additive",
            params=[
                FunctionParam("Feedback Decay", logarithmic=False, min=0.0, max=0.3, default=0.01)
            ]
        ),
        BlendFunction.Sigmoid: BlendFunctionInfo(
            display_name="Sigmoid",
            params=[
                FunctionParam("Feedback Decay",     logarithmic=False, min=0.0, max=0.3, default=0.02),
                FunctionParam("Feedback Steepness", logarithmic=False, default=0.1),
                FunctionParam("Feedback Midpoint",  logarithmic=False, default=0.5)
            ]
        )
    }
    
    
class WarpFunctionInfo(FunctionInfo):
    """
    Extends FunctionInfo to include a dependency on a specific fractal noise variant.
    """
    def __init__(self, display_name: str, fractal_noise_variant: FractalNoiseVariant, params: List[FunctionParam]):
        super().__init__(display_name, params)
        self.fractal_noise_variant = fractal_noise_variant
        
        
class WarpFunctionRegistry(FunctionRegistry):
    """
    A class that statically stores information about warp functions.
    """
    functions = {
        WarpFunction.Offset: WarpFunctionInfo(
            display_name='Offset',
            fractal_noise_variant=FractalNoiseVariant.Double,
            params=[FunctionParam('Amplitude', logarithmic=True, default=0.05)]
        ),
        WarpFunction.Polar: WarpFunctionInfo(
            display_name='Polar',
            fractal_noise_variant=FractalNoiseVariant.Double,
            params=[
                FunctionParam('Radial Strength', logarithmic=True, default=0.02),
                FunctionParam('Rotation Factor', logarithmic=True, default=0.1)
            ]
        ),
        WarpFunction.Swirl: WarpFunctionInfo(
            display_name='Swirl',
            fractal_noise_variant=FractalNoiseVariant.Deriv,
            params=[
                FunctionParam('Radial Strength', logarithmic=True, default=0.02),
                FunctionParam('Swirl Strength', logarithmic=True, default=0.08),
                FunctionParam('Isolation Factor', logarithmic=True, default=0.0),
            ]
        ),
        WarpFunction.SwirlSigmoid: WarpFunctionInfo(
            display_name='Swirl Sigmoid',
            fractal_noise_variant=FractalNoiseVariant.Deriv,
            params=[
                FunctionParam('Radial Strength', logarithmic=True, default=0.02),
                FunctionParam('Swirl Strength', logarithmic=True, default=0.08),
                FunctionParam('Transition Sharpness', logarithmic=True, default=0.0),
                FunctionParam('Transition Point', logarithmic=False, default=0.5),
            ]
        ),
        WarpFunction.SwirlSigmoidDistorted: WarpFunctionInfo(
            display_name='Swirl Sigmoid Distorted',
            fractal_noise_variant=FractalNoiseVariant.Deriv,
            params=[
                FunctionParam('Radial Strength', logarithmic=True, default=0.02),
                FunctionParam('Swirl Strength', logarithmic=True, default=0.08),
                FunctionParam('Transition Sharpness', logarithmic=True, default=0.0),
                FunctionParam('Transition Point', logarithmic=False, default=0.5),
                FunctionParam('Error Scale', logarithmic=True, default=0.0),
                FunctionParam('Error Threshold', logarithmic=True, default=0.0),
                FunctionParam('Error Midpoint', logarithmic=False, default=0.5),
                FunctionParam('Error Strength', logarithmic=True, default=0.3),
                FunctionParam('Error Speed', logarithmic=True, default=0.3),
            ]
        ),
        WarpFunction.OffsetDeriv: WarpFunctionInfo(
            display_name='Offset Derivatives',
            fractal_noise_variant=FractalNoiseVariant.Deriv,
            params=[
                FunctionParam('Amplitude', logarithmic=True, default=0.02),
            ]
        ),
        WarpFunction.InfiniteMirror: WarpFunctionInfo(
            display_name='Infinite Mirror',
            fractal_noise_variant=FractalNoiseVariant.Deriv,
            params=[
                FunctionParam('Duplication Scale', logarithmic=True, default=0.5),
                FunctionParam('Influence Radius', logarithmic=True, default=0.5),
                FunctionParam('Non-Linearity', logarithmic=True, default=0.0),
                FunctionParam('Base Rotation', logarithmic=True, default=0.0),
                FunctionParam('Time Modulation', logarithmic=True, default=0.0),
                FunctionParam('Frequency', logarithmic=True, default=2.0),
            ]
        ),
        WarpFunction.Test: WarpFunctionInfo(
            display_name='Test',
            fractal_noise_variant=FractalNoiseVariant.Deriv,
            params=[
                FunctionParam('Param1', logarithmic=True, default=0.1),
                FunctionParam('Param2', logarithmic=True, default=0.1),
                FunctionParam('Param3', logarithmic=True, default=0.0),
                FunctionParam('Param4', logarithmic=True, default=0.0),
            ]
        ),
    }
    
    
class PlasmaFractalParams:
    """
    Represents the parameters for a plasma fractal.
    This class stores various attributes that define the settings for a plasma fractal.
    """
    
    def __init__(self):
        """
        Initializes a new instance of the PlasmaFractalParams class with default values.
        """     
        # NOISE
        
        # General noise settings
        self.speed = 1.0
        self.scale = 2.0
        
        # Specific noise settings
        self.noise_algorithm = NoiseAlgorithm.Perlin3D
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
        self.feedback_function = BlendFunction.Linear
        self.feedback_params = BlendFunctionRegistry.get_all_param_defaults(use_string_keys=True)   # Convert enum key to string to simplify serialization
        
        # Warp settings for feedback
        self.warpFunction = WarpFunction.Offset
        self.warpParams = WarpFunctionRegistry.get_all_param_defaults(use_string_keys=True)   # Convert enum key to string to simplify serialization
        self.warpSpeed = 1.0
        self.warpNoiseAlgorithm = NoiseAlgorithm.Perlin3D
        self.warpScale = 1.0
        self.warpOctaves = 1
        self.warpGain = 0.3
        self.warpAmplitude = 1.0  # Assuming a default value for amplitude
        self.warpTimeScaleFactor = 1.0
        self.warpPositionScaleFactor = 2.0
        self.warpRotationAngleIncrement = 0.0
        self.warpTimeOffsetInitial = 42.0
        self.warpTimeOffsetIncrement = 12.0
         
         
    def get_current_feedback_function_info(self) -> BlendFunctionInfo:
        """ Return the current BlendFunctionInfo instance. """
        return BlendFunctionRegistry.get_function_info(self.feedback_function)

    def get_current_feedback_params(self) -> List[float]:
        """ Return the current feedback parameters. """
        return self.feedback_params[self.feedback_function.name]
             
    
    def get_current_warp_function_info(self) -> WarpFunctionInfo:
        """ Return the current WarpFunctionInfo instance. """
        return WarpFunctionRegistry.get_function_info(self.warpFunction)

    def get_current_warp_params(self) -> List[float]:
        """ Return the current warp parameters. """
        return self.warpParams[self.warpFunction.name]

    def apply_defaults(self) -> None:
        """
        Reset all attributes to their default values.
        """
        self.__init__()
    
    #............ Serialization helpers ........................................................................

    def to_dict(self) -> dict:
        """
        Convert the public attributes to a dictionary.

        Returns:
        dict: A dictionary representation of the instance.
        """
        return {key: value for key, value in self.__dict__.items() if not key.startswith('_')}

    @classmethod
    def from_dict(cls, data: dict) -> 'PlasmaFractalParams':
        """
        Create a new instance from a dictionary.
        """
        instance = cls()           # Create a new instance with defaults
        instance.merge_dict(data)  # Merge the dictionary into the instance
        return instance
              
    def merge_dict(self, source: dict) -> None:
        """
        Update the instance with the values from a dictionary.
        Only sets attributes from the dictionary that already exist in the instance.
        Makes sure that the types of the values match the types of the attributes.
        """
        merged = type_safe_json_merge(self.to_dict(), source, convert_scalar=convert_json_scalar)
        
        for key, value in merged.items():
            setattr(self, key, value)
