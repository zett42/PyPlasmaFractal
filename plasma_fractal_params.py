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

class WarpFunction(Enum):
    """
    Enumeration of warp functions used for modifying noise fields.
    """
    Offset = auto()
    Polar = auto()
    OffsetDeriv = auto()
    Swirl = auto()
    Test = auto()

    # Default fallback value for missing keys (due to serialization/deserialization issues)
    @staticmethod
    def _missing_(value):
        return WarpFunction.Offset
    
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

    def __init__(self, fractal_noise_variant: FractalNoiseVariant, params: List[WarpFunctionParam] = []):

       # Check if the number of provided parameters exceeds the maximum allowed
        if len(params) > self.MAX_WARP_PARAMS:
            raise ValueError(f"Too many parameters: {len(params)} provided, but the maximum is {self.MAX_WARP_PARAMS}")

        self.fractal_noise_variant = fractal_noise_variant
        self.params = params


# Dictionary that maps warp functions to their respective information
# NOTE: adjust MAX_WARP_PARAMS according to the maximum number of parameters for any warp function

WARP_FUNCTION_INFOS = {
    WarpFunction.Offset: WarpFunctionInfo(
        FractalNoiseVariant.Double,
        params=[
            WarpFunctionParam('Amplitude', logarithmic=True, default=0.05),
        ]
    ),
    WarpFunction.Polar: WarpFunctionInfo(
        FractalNoiseVariant.Double, 
        params=[
            WarpFunctionParam('Radial Strength', logarithmic=True, default=0.02),
            WarpFunctionParam('Rotation Factor', logarithmic=True, default=0.1),
        ]
    ),
    WarpFunction.Swirl: WarpFunctionInfo(
        FractalNoiseVariant.Deriv, 
        params=[
            WarpFunctionParam('Radial Strength', logarithmic=True, default=0.02),
            WarpFunctionParam('Swirl Strength', logarithmic=True, default=0.08),
            WarpFunctionParam('Isolation Factor', logarithmic=True, default=0.0),
        ]
    ),    
    WarpFunction.OffsetDeriv: WarpFunctionInfo(
        FractalNoiseVariant.Deriv, 
        params=[
            WarpFunctionParam('Amplitude', logarithmic=True, default=0.02),
        ]
    ),
    WarpFunction.Test: WarpFunctionInfo(
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
            warp_func: [param.default for param in WARP_FUNCTION_INFOS[warp_func].params]
            for warp_func in WarpFunction
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
            'warpFunction': WarpFunction.Offset,
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

    def __setstate__(self, state):
        """
        Customize the deserialization process to ensure the object's attributes align with
        the current class definition. This method applies default values to missing keys, updates
        the object's state from the provided serialized data, and issues warnings for any 
        unrecognized keys.

        Parameters:
        - state (dict): The dictionary representing the serialized state of the object.

        This method ensures smooth updates and integrity checks during object deserialization,
        aiding in backward compatibility and error identification in serialized data management.
        """
        defaults = self.get_default_values()

        for key, default_value in defaults.items():
            try:
                self.__dict__[key] = state.get(key, default_value)
            except ValueError:
                self.__dict__[key] = default_value
