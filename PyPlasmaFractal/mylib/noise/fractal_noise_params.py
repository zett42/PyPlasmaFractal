from typing import *
from PyPlasmaFractal.mylib.config.serializable_config import SerializableConfig
from PyPlasmaFractal.mylib.config.function_info import ParamType, StructuredParamType, FloatParamType, IntParamType, DynamicEnumType 

class FractalNoiseParams(SerializableConfig):
    """
    Represents common parameters for fractal noise generation and animation.
    """
    def __init__(self):
        super().__init__() 
        
        # Algorithm control
        self.noise_algorithm = 'perlin_3d'  # This is fine since it's defined in ALLOWED_ALGORITHMS
        self.octaves = 1
        self.gain = 0.5
        
        # Per-octave settings
        self.time_scale_factor = 1.0
        self.position_scale_factor = 2.0
        self.rotation_angle_increment = 0.0
        self.time_offset_increment = 12.0

        # Scale settings
        self.scale = 2.0
        self.speed = 1.0
        self.time_offset = 0.0


class NoiseAlgorithmType(DynamicEnumType[str]):
    """
    A class for handling noise algorithm parameter types.
    This is a derived class just to be able to identify the type dynamically.
    """
    @property
    def name(self) -> str:
        return "noise_algorithm"


class FractalNoiseParamsType(StructuredParamType):
    """
    Describes FractalNoiseParams instances.
    """
    
    @property
    def name(self) -> str:
        return "fractal_noise_params"
    
    def create_instance(self) -> FractalNoiseParams:
        return FractalNoiseParams()
    
    def describe_attributes(self) -> Dict[str, 'ParamType']:
        return {
            'noise_algorithm': NoiseAlgorithmType({'perlin_3d', 'simplex_perlin_3d', 'cellular_3d'}),
            'octaves': IntParamType(min=1, max=12),
            'gain': FloatParamType(min=0.0, max=1.0),
            'time_scale_factor': FloatParamType(min=0.1, max=10.0),
            'position_scale_factor': FloatParamType(min=0.1, max=10.0),
            'rotation_angle_increment': FloatParamType(min=0.0, max=6.28318530718),  # 2 * pi
            'time_offset_increment': FloatParamType(min=0.0, max=20.0),
            'scale': FloatParamType(min=0.1, max=10.0),
            'speed': FloatParamType(min=0.1, max=10.0),
            'time_offset': FloatParamType(min=0.0, max=100.0)
        }
