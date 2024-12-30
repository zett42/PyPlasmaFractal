import pytest
from PyPlasmaFractal.mylib.config.function_glsl_generator import GlslTypeMapper, GlslGenerator
from PyPlasmaFractal.mylib.config.function_registry import FunctionInfo, FunctionParam, ParamType
from enum import Enum

@pytest.fixture
def test_function():
    return FunctionInfo({
        "display_name": "Test Function",
        "description": "A test function.",
        "params": [
            {"name": "param1", "display_name": "Param 1", "param_type": ParamType.FLOAT, "default": 0.0, "min": 0.0, "max": 1.0},
            {"name": "param2", "display_name": "Param 2", "param_type": ParamType.COLOR, "default": [1.0, 1.0, 1.0, 1.0]}
        ]
    })


def test_glsl_type_mapper():
    
    assert GlslTypeMapper.get_glsl_type(ParamType.FLOAT) == "float"
    assert GlslTypeMapper.get_glsl_type(ParamType.COLOR) == "vec4"

    with pytest.raises(ValueError):
        NewParamType = Enum('NewParamType', [(name, member.value) for name, member in ParamType.__members__.items()] + [('SOME_NEW_TYPE', 99)])
        GlslTypeMapper.get_glsl_type(NewParamType.SOME_NEW_TYPE)


def test_get_uniform_name():
    
    assert GlslGenerator.get_uniform_name("param") == "u_param"


def test_get_function_params_uniform_names(test_function):
    
    uniform_names = GlslGenerator.get_function_params_uniform_names(test_function)
    assert uniform_names == ["u_param1", "u_param2"]


def test_generate_param_uniform():
    
    param = FunctionParam({"name": "param", "display_name": "Param", "param_type": ParamType.FLOAT, "default": 0.0, "min": 0.0, "max": 1.0})
    uniform_declaration = GlslGenerator.generate_param_uniform(param)
    assert uniform_declaration == "uniform float u_param;"


def test_generate_function_params_uniforms(test_function):
    
    uniforms = GlslGenerator.generate_function_params_uniforms(test_function)
    expected_uniforms = "uniform float u_param1;\nuniform vec4 u_param2;"
    assert uniforms == expected_uniforms


def test_generate_function_args(test_function):
    
    args = GlslGenerator.generate_function_args(test_function)
    assert args == "u_param1, u_param2"
