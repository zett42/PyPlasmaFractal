from typing import *

from PyPlasmaFractal.mylib.config.serializable_config import SerializableConfig


class FractalNoiseParams(SerializableConfig):
    """
    Represents common parameters for fractal noise generation and animation.
    """
    def __init__(self):
        super().__init__() 
        
        # Algorithm control
        self.noise_algorithm = ''
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
