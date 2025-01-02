from typing import *
from PyPlasmaFractal.mylib.config.serializable_config import SerializableConfig
from PyPlasmaFractal.mylib.config.function_registry import FloatParamType, IntParamType, ParamType

class FractalNoiseParams(SerializableConfig):
    """
    Represents common parameters for fractal noise generation and animation.
    """
    def __init__(self):
        super().__init__() 
        
        # Algorithm control
        self.noise_algorithm = 'perlin_3d'
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


class NoiseAlgorithmType(ParamType):
    """
    A class for handling noise algorithm parameter types.
    """
    
    def __init__(self, allowed_values: List[str]):
        self.allowed_values = allowed_values
    
    @property
    def name(self) -> str:
        return "noise_algorithm"
    
    def create_default(self) -> str:
        return self.allowed_values[0] if self.allowed_values else ""
    
    def convert(self, value: Any, attributes: Dict[str, Any]) -> str:
        if value not in self.allowed_values:
            raise ValueError(f"Value {value} is not a valid noise algorithm")
        return value
    
    def describe_attributes(self) -> Dict[str, ParamType]:
        return {}
    

class FractalNoiseParamsType(ParamType):
    """
    Parameter type handler for FractalNoiseParams instances.
    """
    
    @property
    def name(self) -> str:
        return "fractal_noise_params"
    
    def create_default(self) -> FractalNoiseParams:
        return FractalNoiseParams()
    
    def convert(self, value: Any, constrains: Dict[str, Any]) -> FractalNoiseParams:
        
        if isinstance(value, FractalNoiseParams):
            return value
        
        if isinstance(value, dict):
            params = FractalNoiseParams()
            for key, val in value.items():
                if hasattr(params, key):
                    setattr(params, key, val)
            return params
            
        raise ValueError(f"Cannot convert {value} to FractalNoiseParams")

    def describe_attributes(self) -> Dict[str, 'ParamType']:
        return {
            'noise_algorithm': NoiseAlgorithmType(['perlin_3d', 'simplex_perlin_3d', 'cellular_3d']),
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
