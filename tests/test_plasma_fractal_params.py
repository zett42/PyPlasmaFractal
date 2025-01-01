import pytest
from unittest.mock import Mock
from PyPlasmaFractal.plasma_fractal_params import PlasmaFractalParams
from PyPlasmaFractal.plasma_fractal_types import ShaderFunctionType
from PyPlasmaFractal.mylib.config.function_registry import FunctionRegistry, FunctionInfo

@pytest.fixture
def mock_registries():
    registries = {}
    mock_function_info = FunctionInfo({
        'display_name': 'Test Function',
        'description': 'Test function description',
        'params': []
    })
    
    for shader_type in ShaderFunctionType:
        mock_registry = Mock(spec=FunctionRegistry)
        mock_registry.get_function_keys.return_value = ['func1', 'func2']
        mock_registry.get_function_info.return_value = mock_function_info
        mock_registry.get_all_param_defaults.return_value = {'func1': [], 'func2': []}
        registries[shader_type] = mock_registry
    return registries

@pytest.fixture
def params(mock_registries):
    return PlasmaFractalParams(mock_registries)

def test_initialization(params):
    """Test if the class initializes with correct default values"""
    assert params.speed == 1.0
    assert params.brightness == 1.0
    assert params.contrast_steepness == 10.0
    assert params.contrast_midpoint == 0.5
    assert not params.enable_feedback

def test_noise_parameters(params):
    """Test if noise parameters are properly initialized"""
    assert params.noise.noise_algorithm == 'func1'
    assert params.warp_noise.noise_algorithm == 'func1'
    assert params.warp_noise.gain == 0.3
    assert params.warp_noise.time_offset == 42.0

def test_getter_methods(params):
    """Test if getter methods return correct values"""
    blend_info = params.get_current_feedback_blend_function_info()
    assert isinstance(blend_info, FunctionInfo)
    
    warp_info = params.get_current_warp_function_info()
    assert isinstance(warp_info, FunctionInfo)
    
    color_info = params.get_current_color_function_info()
    assert isinstance(color_info, FunctionInfo)

def test_serialization(params):
    """Test serialization to dictionary"""
    params_dict = params.to_dict()
    assert isinstance(params_dict, dict)
    assert '_shader_function_registries' not in params_dict
    assert 'speed' in params_dict
    assert 'brightness' in params_dict
    assert 'noise' in params_dict

def test_merge_dict(params):
    """Test merging dictionary into parameters"""
    new_values = {
        'speed': 2.0,
        'brightness': 0.5,
        'contrast_steepness': 5.0,
        'invalid_key': 'should_be_ignored'
    }
    params.merge_dict(new_values)
    
    assert params.speed == 2.0
    assert params.brightness == 0.5
    assert params.contrast_steepness == 5.0
    assert not hasattr(params, 'invalid_key')

def test_apply_defaults(params):
    """Test resetting to default values"""
    params.speed = 2.0
    params.brightness = 0.5
    params.apply_defaults()
    
    assert params.speed == 1.0
    assert params.brightness == 1.0

def test_noise_defaults_restore(params):
    """Test that noise parameters are properly restored to defaults"""
    # Modify noise parameters
    params.noise.noise_algorithm = 'func2'
    params.noise.gain = 0.8
    params.warp_noise.noise_algorithm = 'func2'
    params.warp_noise.time_offset = 100.0
    
    # Reset to defaults
    params.apply_defaults()
    
    # Verify noise parameters are back to defaults
    assert params.noise.noise_algorithm == 'func1'
    assert params.warp_noise.noise_algorithm == 'func1'
    assert params.warp_noise.gain == 0.3
    assert params.warp_noise.time_offset == 42.0
