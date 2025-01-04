import PyPlasmaFractal.mylib.gui.imgui_helper as ih
from PyPlasmaFractal.plasma_fractal_params import PlasmaFractalParams
from PyPlasmaFractal.mylib.config.function_registry import FunctionRegistry
from PyPlasmaFractal.gui.utils.common_controls import noise_controls

class NoiseTab:
    """
    Manages the UI controls for adjusting noise-related settings in the plasma fractal visualization.
    """

    def __init__(self, noise_function_registry: FunctionRegistry):
        
        self.noise_function_registry = noise_function_registry
        self.noise_settings_open = True
        

    def update(self, params: PlasmaFractalParams):

        with ih.resized_items(-160):
            if ih.collapsing_header("Noise Settings", self, attr='noise_settings_open'):
                noise_controls(params.noise, 'NoiseTab', self.noise_function_registry)
