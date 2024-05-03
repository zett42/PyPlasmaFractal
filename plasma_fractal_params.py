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

    # Define the maximum allowed number of parameters for any warp function. This needs to be hardcoded, because shader uniforms are fixed-size arrays.
    MAX_WARP_PARAMS: int = 4

    def __init__(self, fractal_noise_variant: FractalNoiseVariant, params: List[WarpFunctionParam] = [], display_name: str = None):

       # Check if the number of provided parameters exceeds the maximum allowed
        if len(params) > self.MAX_WARP_PARAMS:
            raise ValueError(f"Too many parameters: {len(params)} provided, but the maximum is {self.MAX_WARP_PARAMS}")

        self.display_name = display_name
        self.fractal_noise_variant = fractal_noise_variant
        self.params = params


# Dictionary that maps warp functions to their respective information
# NOTE: adjust MAX_WARP_PARAMS according to the maximum number of parameters for any warp function

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
    'OffsetDeriv': WarpFunctionInfo(
        FractalNoiseVariant.Deriv, 
        params=[
            WarpFunctionParam('Amplitude', logarithmic=True, default=0.02),
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

class PlasmaFractalParams:
    """
    Represents the parameters for a plasma fractal.

    This class stores various attributes that define the settings for a plasma fractal.
    """

    def __init__(self, use_defaults=False):
        """
        Initializes a new instance of the PlasmaFractalParams class.

        Args:
            use_defaults (bool, optional): Whether to apply default values to the attributes. Defaults to False.
        """
        # Initialize all attributes to None to ensure they are defined (helps code completion in IDEs)
        
        # General settings
        self.paused = None
        
        # NOISE
        # General noise settings
        self.speed = None
        self.scale = None
        
        # Specific noise settings
        self.noise_algorithm = None
        self.octaves = None
        self.gain = None
        self.amplitude = None
        self.timeScaleFactor = None
        self.positionScaleFactor = None
        self.rotationAngleIncrement = None
        self.timeOffsetIncrement = None
        
        # Contrast settings for noise
        self.contrastSteepness = None
        self.contrastMidpoint = None
        
        # FEEDBACK
        # General Feedback Settings
        self.enable_feedback = None
        self.feedback_decay = None
        
        # Warp settings for feedback
        self.warpFunction = None
        self.warpParams = None
        self.warpSpeed = None
        self.warpNoiseAlgorithm = None
        self.warpScale = None
        self.warpOctaves = None
        self.warpGain = None
        self.warpAmplitude = None
        self.warpTimeScaleFactor = None
        self.warpPositionScaleFactor = None
        self.warpRotationAngleIncrement = None
        self.warpTimeOffsetInitial = None
        self.warpTimeOffsetIncrement = None
        
        # GUI State flags
        self.general_settings_open = None
        self.noise_settings_open = None
        self.fractal_settings_open = None
        self.output_settings_open = None
        self.feedback_general_settings_open = None
        self.feedback_warp_general_settings_open = None
        self.feedback_warp_noise_settings_open = None
        self.feedback_warp_octave_settings_open = None
        self.feedback_warp_contrast_settings_open = None
       
        # Apply default settings if requested
        if use_defaults:
            self.apply_defaults()

    def get_default_values(self):
        """
        Returns a dictionary containing the default values for the parameters used in the plasma fractal generator.
        
        Returns:
            dict: A dictionary containing the default values for the parameters.
        """

        warp_params_defaults = {
            key: [param.default for param in WARP_FUNCTION_INFOS[key].params]
            for key in WARP_FUNCTION_INFOS
        }


        return {
            # General settings
            'paused': False,
            
            # NOISE
            # General noise settings
            'speed': 1.0,
            'scale': 2.0,
            
            # Specific noise settings
            'noise_algorithm': NoiseAlgorithm.Perlin3D,
            'octaves': 1,
            'gain': 0.5,
            'timeScaleFactor': 1.3,
            'positionScaleFactor': 2.0,
            'rotationAngleIncrement': 0.0,
            'timeOffsetIncrement': 12.0,
            
            # Output adjustment for noise
            'brightness': 1.0,
            'contrastSteepness': 10.0,
            'contrastMidpoint': 0.5,
            
            # FEEDBACK
            # General feedback settings
            'enable_feedback': False,
            'feedback_decay': 0.01,
            
            # Warp settings for feedback
            'warpSpeed': 1.0,
            'warpScale': 1.0,
            'warpNoiseAlgorithm': NoiseAlgorithm.Perlin3D,
            'warpOctaves': 1,
            'warpGain': 0.5,
            'warpTimeScaleFactor': 1.0,
            'warpPositionScaleFactor': 2.0,
            'warpRotationAngleIncrement': 0.0,
            'warpTimeOffsetInitial': 42.0,
            'warpTimeOffsetIncrement': 12.0,
            'warpFunction': list(WARP_FUNCTION_INFOS.keys())[0],
            'warpParams': warp_params_defaults,

            # GUI State flags
            'general_settings_open': True,
            'noise_settings_open': True,
            'fractal_settings_open': True,
            'output_settings_open': True,
            'feedback_general_settings_open': True,
            'feedback_warp_general_settings_open': True,
            'feedback_warp_noise_settings_open': True,
            'feedback_warp_effect_settings_open': True,
            'feedback_warp_octave_settings_open': True,
            'feedback_warp_contrast_settings_open': True
        }
    
    
    def get_warp_function_names(self) -> List[str]:
        """
        Gets the names of the available warp functions.

        Returns:
            List[str]: A list of the names of the available warp functions.
        """
        return list(WARP_FUNCTION_INFOS.keys())


    def get_current_warp_function_info(self) -> WarpFunctionInfo:
        """
        Gets the WarpFunctionInfo object for the current warp function.

        Returns:
            WarpFunctionInfo: The WarpFunctionInfo object for the current warp function.
        """
        return WARP_FUNCTION_INFOS[self.warpFunction]

    def get_current_warp_params(self) -> List[float]:
        """
        Gets the current warp parameters for the selected warp function.

        Returns:
            List[float]: The current warp parameter values.
        """
        return self.warpParams[self.warpFunction]

    
    def apply_defaults(self):
        """
        Applies default values to the attributes of the object.

        This method retrieves the default values for each attribute from the
        `get_default_values` method and sets them using the `setattr` function.

        Args:
            None

        Returns:
            None
        """
        defaults = self.get_default_values()
        for key, value in defaults.items():
            setattr(self, key, value)


    def to_dict(self):
        """Convert all attributes of the class to a dictionary."""
        return {attr: getattr(self, attr) for attr in self.__dict__ if not attr.startswith('_')}

    @classmethod
    def from_dict(cls, data):
        """Initialize the class from a dictionary."""
        obj = cls()
        for key, value in data.items():
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
