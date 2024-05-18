import pytest
from typing import *
from tempfile import TemporaryDirectory
from PyPlasmaFractal.mylib.config.dict_text_file_storage import DictTextFileStorage
from PyPlasmaFractal.mylib.gfx.shader_template_system import resolve_shader_template

# Test data setup for various test scenarios
mock_sources = {
    'main_shader.glsl': 'void main() { baseFunction(); commonFunction(); }\n#include "base_shader.glsl"',
    'base_shader.glsl': 'void baseFunction() {}\n#include "common_shader.glsl"',
    'common_shader.glsl': 'void commonFunction() {}',
    'circular_a.glsl': 'Circle A\n#include "circular_b.glsl"',
    'circular_b.glsl': 'Circle B\n#include "circular_a.glsl"',
    'template_shader.glsl': 'void light() { return <LIGHT_TYPE>; }\nThis is the color <COLOR>\n#apply_template "light_type_shader.glsl", LIGHT_TYPE=<LIGHT_TYPE>',
    'light_type_shader.glsl': 'Light type is <LIGHT_TYPE>'
}

@pytest.fixture
def storage():
    with TemporaryDirectory() as temp_dir:
        storage = DictTextFileStorage()
        for filename, content in mock_sources.items():
            storage.save(content, filename)
        yield storage


@pytest.mark.parametrize("filename,expected_output", [
    ("main_shader.glsl", 'void main() { baseFunction(); commonFunction(); }\nvoid baseFunction() {}\nvoid commonFunction() {}'),  # Main shader with nested includes
    ("common_shader.glsl", 'void commonFunction() {}')  # Test with no includes
], ids=[
    "nested_includes", "no_includes"
])
def test_resolve_shader_includes(storage, filename, expected_output):
    
    resolved_shader_code = resolve_shader_template(filename, storage)
    assert resolved_shader_code == expected_output


# Test cases for errors and limits
def test_missing_include(storage):
    
    with pytest.raises(Exception, match='Error loading source from "non_existent.glsl"'):
        resolve_shader_template('non_existent.glsl', storage)


def test_circular_include(storage):
    
    with pytest.raises(Exception, match='Error in "circular_b.glsl": Circular include detected.\n  #include "circular_a.glsl"'):
        resolve_shader_template('circular_a.glsl', storage)


def test_depth_limit(storage):
    
    max_include_depth = 2

    storage.save('Level 0\n#include "deep_shader_1.glsl"', 'deep_shader_0.glsl')
    storage.save('Level 1\n#include "deep_shader_2.glsl"', 'deep_shader_1.glsl')
    storage.save('Level 2', 'deep_shader_2.glsl')

    # This function should not attempt to include 'deep_shader_3.glsl' if the depth limit works correctly
    with pytest.raises(Exception, match=f'Maximum include depth of {max_include_depth} exceeded'):
        resolve_shader_template('deep_shader_0.glsl', storage, max_include_depth=max_include_depth)

    # Ensure 'deep_shader_3.glsl' was not accessed
    assert 'deep_shader_3.glsl' not in storage.list(), "Attempted to access a depth exceeding the limit"


# Test for template parameter resolution within the top-level shader source
def test_template_parameter_resolution(storage):
    
    expected_output = 'void light() { return POINT_LIGHT; }\nThis is the color red\nLight type is POINT_LIGHT'
    resolved_shader_code = resolve_shader_template('template_shader.glsl', storage, {'LIGHT_TYPE': 'POINT_LIGHT', 'COLOR': 'red'})
    assert resolved_shader_code == expected_output
