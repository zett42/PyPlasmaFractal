from json import JSONEncoder
import json
from typing import *
from enum import Enum, auto

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

class FeedbackBlendMode(Enum):
    """
    Enumeration of feedback blend modes.
    """
    Linear = auto()
    Additive = auto()
    Sigmoid = auto()

class WarpFunctionParam:
    """
    Information about a parameter used in warp functions and how to represent it in the UI.
    """
    def __init__(self, displayName: str, min = 0.0, max = 1.0, logarithmic: bool = False, default = 0.5):
        self.displayName = displayName
        self.min = min
        self.max = max
        self.logarithmic = logarithmic
        self.default = default

class WarpFunctionInfo:
    """
    Contains information about a warp function, including its parameters and dependency on specific fractal noise variant.
    """

    def __init__(self, fractal_noise_variant: FractalNoiseVariant, params: List[WarpFunctionParam] = [], display_name: str = None):

        self.display_name = display_name
        self.fractal_noise_variant = fractal_noise_variant
        self.params = params


# Dictionary that maps warp functions to their respective information

WARP_FUNCTION_INFOS = {
    'Offset': WarpFunctionInfo(
        FractalNoiseVariant.Double,
        params=[
            WarpFunctionParam('Amplitude', logarithmic=True, default=0.05),
        ]
    ),
    'Polar': WarpFunctionInfo(
        FractalNoiseVariant.Double, 
        params=[
            WarpFunctionParam('Radial Strength', logarithmic=True, default=0.02),
            WarpFunctionParam('Rotation Factor', logarithmic=True, default=0.1),
        ]
    ),    
    'Swirl': WarpFunctionInfo(
        FractalNoiseVariant.Deriv, 
        params=[
            WarpFunctionParam('Radial Strength', logarithmic=True, default=0.02),
            WarpFunctionParam('Swirl Strength', logarithmic=True, default=0.08),
            WarpFunctionParam('Isolation Factor', logarithmic=True, default=0.0),
        ]
    ),    
    'SwirlSigmoid': WarpFunctionInfo(
        FractalNoiseVariant.Deriv, 
        params=[
            WarpFunctionParam('Radial Strength', logarithmic=True, default=0.02),
            WarpFunctionParam('Swirl Strength', logarithmic=True, default=0.08),
            WarpFunctionParam('Transition Sharpness', logarithmic=True, default=0.0),
            WarpFunctionParam('Transition Point', logarithmic=False, default=0.5),
        ]
    ),
    'OffsetDeriv': WarpFunctionInfo(
        FractalNoiseVariant.Deriv, 
        params=[
            WarpFunctionParam('Amplitude', logarithmic=True, default=0.02),
        ]
    ),
    'InfiniteMirror': WarpFunctionInfo(
        FractalNoiseVariant.Deriv, 
        params=[
            WarpFunctionParam('Duplication Scale', logarithmic=True, default=0.5),
            WarpFunctionParam('Influence Radius', logarithmic=True, default=0.5),
            WarpFunctionParam('Non-Linearity', logarithmic=True, default=0.0),
            WarpFunctionParam('Base Rotation', logarithmic=True, default=0.0),
            WarpFunctionParam('Time Modulation', logarithmic=True, default=0.0),
            WarpFunctionParam('Frequency', logarithmic=True, default=2.0),
        ]
    ),
    'Test': WarpFunctionInfo(
        FractalNoiseVariant.Deriv, 
        params=[
            WarpFunctionParam('Param1', logarithmic=True, default=0.1),
            WarpFunctionParam('Param2', logarithmic=True, default=0.1),
            WarpFunctionParam('Param3', logarithmic=True, default=0.0),
            WarpFunctionParam('Param4', logarithmic=True, default=0.0),
        ]
    ),
}

MAX_WARP_PARAMS = max(len(info.params) for info in WARP_FUNCTION_INFOS.values())

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
        # General Feedback Settings
        self.enable_feedback = False
        self.feedback_blend_mode = FeedbackBlendMode.Linear
        self.feedback_decay = 0.01
        self.feedback_param1 = 0.1   # TODO: Create dictionary of parameters, similar to warpParams
        self.feedback_param2 = 0.5
        
        # Warp settings for feedback
        self.warpFunction = list(WARP_FUNCTION_INFOS.keys())[0]   # Default to the first warp function
        self.warpParams = {    # A dictionary that maps warp function names to arrays of parameters
            key: [param.default for param in WARP_FUNCTION_INFOS[key].params]
            for key in WARP_FUNCTION_INFOS
        }
        self.warpSpeed = 1.0
        self.warpNoiseAlgorithm = NoiseAlgorithm.Perlin3D
        self.warpScale = 1.0
        self.warpOctaves = 1
        self.warpGain = 0.5
        self.warpAmplitude = 1.0  # Assuming a default value for amplitude
        self.warpTimeScaleFactor = 1.0
        self.warpPositionScaleFactor = 2.0
        self.warpRotationAngleIncrement = 0.0
        self.warpTimeOffsetInitial = 42.0
        self.warpTimeOffsetIncrement = 12.0
         
    
    def get_warp_function_names(self) -> List[str]:
        return list(WARP_FUNCTION_INFOS.keys())

    def get_current_warp_function_info(self) -> WarpFunctionInfo:
        return WARP_FUNCTION_INFOS[self.warpFunction]

    def get_current_warp_params(self) -> List[float]:
        return self.warpParams[self.warpFunction]
    
    def get_max_warp_params(self) -> int:
        return MAX_WARP_PARAMS

    
    def update(self, new_params: 'PlasmaFractalParams'):
        """
        Update the instance attributes with another instance's attributes.

        Args:
        new_params (PlasmaFractalParams): An instance of PlasmaFractalParams with new values.
        """
        for key, value in vars(new_params).items():
            if hasattr(self, key):
                setattr(self, key, value)    # TODO: dictionary attributes like warpParams need special handling (recursion)


    #............ Serialization methods ........................................................................

    def to_dict(self):
        """Convert all public attributes of the class to a dictionary."""
        return {attr: getattr(self, attr) for attr in self.__dict__ if not attr.startswith('_')}

    @classmethod
    def from_dict(cls, data):
        """Initialize the class from a dictionary, setting only attributes that already exist after default construction, 
        with special handling for dictionary attributes (like the warpParams attribute)."""
        obj = cls()
        for key, value in data.items():
            if hasattr(obj, key):
                current_attribute = getattr(obj, key)
                # Check if both are dictionaries and then merge them based on existing keys
                if isinstance(current_attribute, dict) and isinstance(value, dict):
                    for sub_key in current_attribute:
                        if sub_key in value:
                            current_attribute[sub_key] = value[sub_key]
                else:
                    setattr(obj, key, value)
        return obj

    def to_json(self):
        """Serializes the object to a JSON formatted str."""

        # Define the custom JSON encoder for complex types
        class CustomEncoder(JSONEncoder):
            def default(self, obj):
                if isinstance(obj, Enum):
                    return {"__enum__": str(obj)}
                elif isinstance(obj, PlasmaFractalParams):
                    return obj.to_dict()  # Serialize PlasmaFractalParams using its to_dict method
                return JSONEncoder.default(self, obj)

        return json.dumps(self, cls=CustomEncoder, indent=4)

    @classmethod
    def from_json(cls, json_str):
        """Deserializes JSON formatted str to an instance of the class."""

        def decode_custom(dct):
            if "__enum__" in dct:
                enum_name, member_name = dct["__enum__"].split('.')
                return getattr(globals()[enum_name], member_name)
            return dct

        return cls.from_dict(json.loads(json_str, object_hook=decode_custom))
