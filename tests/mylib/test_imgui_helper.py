import pytest
from typing import *
from enum import Enum, auto
import mylib.imgui_helper as ih

#------------------------------------------------------------------------------------------------------------------------------------------
# Test setup classes

# Assuming the same enum and class definitions
class Color(Enum):
    RED = auto()
    GREEN = auto()
    BLUE = auto()

class TestObject:
    def __init__(self):
        self.color = Color.RED
        self.color_values = [Color.RED, Color.RED, Color.RED]
        self.value = 0
        self.int_values = [1, 2, 3] 
        self.float_values = [1.0, 2.0, 3.0] 
        self.float_dict = {'value1': 1.0, 'value2': 2.0, 'value3': 3.0}
        self.active = False
        self.active_values = [False, False, False]
        self.text = "initial"

# Test setup
@pytest.fixture
def test_obj():
    return TestObject()


#------------------------------------------------------------------------------------------------------------------------------------------

def test_collapsing_header(test_obj, mocker):
    
    expected_value = True

    # Mock the imgui.collapsing_header function
    mocker.patch('mylib.imgui_helper.imgui.collapsing_header', return_value=(expected_value, None))

    # Assume the initial value is False
    test_obj.active = False

    # Invoke the collapsing_header function
    result = ih.collapsing_header('Collapsing Header', test_obj, 'active')

    # Assert the active attribute was updated correctly
    assert test_obj.active is expected_value, f"The active state should be updated to {expected_value}"

    # Assert the result matches the expected value
    assert result is expected_value, f"The result should be {expected_value}"
    
#------------------------------------------------------------------------------------------------------------------------------------------

def test_slider_int(test_obj, mocker):

    expected_value = 50

    # Mock the imgui.slider_int function
    mocker.patch('mylib.imgui_helper.imgui.slider_int', return_value=(True, expected_value))
    
    # Invoke the slider_int function
    ih.slider_int('Int Slider', test_obj, 'value', min_value=0, max_value=100)
    
    # Assert the value was updated correctly
    assert test_obj.value == expected_value, f"The value should be updated to {expected_value}"

#------------------------------------------------------------------------------------------------------------------------------------------

def test_slider_int_with_list(test_obj, mocker):

    expected_value = 50

    # Mock the slider_int function to simulate slider interaction
    mocker.patch('mylib.imgui_helper.imgui.slider_int', return_value=(True, expected_value))
    
    # Invoke the slider_int function for indexed interaction if applicable
    test_index = 1
    ih.slider_int('Int Slider', test_obj, 'int_values', index=test_index, min_value=0, max_value=100)

    assert test_obj.int_values[test_index] == expected_value, f"The value at index {test_index} should be updated to {expected_value}"

#------------------------------------------------------------------------------------------------------------------------------------------

def test_slider_float(test_obj, mocker):

    expected_value = 50.5  

    # Mock the imgui.slider_float function
    mocker.patch('mylib.imgui_helper.imgui.slider_float', return_value=(True, expected_value))
    
    # Invoke the slider_float function
    ih.slider_float('Float Slider', test_obj, 'value', min_value=0.0, max_value=100.0)
    
    # Assert the value was updated correctly
    assert test_obj.value == expected_value, f"The value should be updated to {expected_value}"

#------------------------------------------------------------------------------------------------------------------------------------------

def test_slider_float_with_list(test_obj, mocker):

    expected_value = 50.5  

    # Mock the imgui.slider_float function
    mocker.patch('mylib.imgui_helper.imgui.slider_float', return_value=(True, expected_value))
    
    # Invoke the slider_float function with an index argument
    test_index = 1
    ih.slider_float("Float Slider for Index", test_obj, 'float_values', index=test_index, min_value=0.0, max_value=100.0)
    
    # Assert the value was updated correctly
    assert test_obj.float_values[test_index] == expected_value, f"The value at index {test_index} should be updated to {expected_value}"

#------------------------------------------------------------------------------------------------------------------------------------------

def test_slider_float_with_dict(test_obj, mocker):

    expected_value = 50.5  

    # Mock the imgui.slider_float function
    mocker.patch('mylib.imgui_helper.imgui.slider_float', return_value=(True, expected_value))
    
    # Invoke the slider_float function with a dictionary attribute
    test_key = 'value2'
    ih.slider_float("Float Slider for Dict", test_obj, 'float_dict', index=test_key, min_value=0.0, max_value=100.0)
    
    # Assert the value was updated correctly
    assert test_obj.float_dict[test_key] == expected_value, f"The value for key '{test_key}' should be updated to {expected_value}"

#------------------------------------------------------------------------------------------------------------------------------------------

def test_slider_float_direct_index(test_obj, mocker):

    expected_value = 50.5  

    # Mock the imgui.slider_float function
    mocker.patch('mylib.imgui_helper.imgui.slider_float', return_value=(True, expected_value))
    
    # Define the index to interact directly with test_obj's float_values attribute
    test_index = 1
    
    # Since we're not specifying 'attr', we assume the 'obj' itself is a list that can be indexed.
    # We directly interact with the test_obj.float_values for this test to simulate that scenario.
    ih.slider_float("Float Slider Direct Index", test_obj.float_values, index=test_index, min_value=0.0, max_value=100.0)
    
    # Assert the value was updated correctly
    assert test_obj.float_values[test_index] == expected_value, f"The value at index {test_index} should be updated to {expected_value}"

#------------------------------------------------------------------------------------------------------------------------------------------

def test_checkbox(test_obj, mocker):

    expected_value = True

    # Mock the imgui.checkbox function
    mocker.patch('mylib.imgui_helper.imgui.checkbox', return_value=(True, expected_value))
    
    # Assume the initial value is False
    test_obj.active = False
    
    # Invoke the checkbox function
    ih.checkbox('Active Checkbox', test_obj, 'active')
    
    # Assert the active attribute was updated correctly
    assert test_obj.active is expected_value, f"The active state should be updated to {expected_value}"

#------------------------------------------------------------------------------------------------------------------------------------------

def test_checkbox_with_list(test_obj, mocker):

    expected_value = True

    # Mock the checkbox function to simulate checkbox being checked
    mocker.patch('mylib.imgui_helper.imgui.checkbox', return_value=(True, expected_value))
    
    # Invoke the checkbox function for indexed interaction if applicable
    test_index = 2
    ih.checkbox('Active Checkbox', test_obj, 'active_values', index=test_index)
    assert test_obj.active_values[test_index] is expected_value, f"The active state at index {test_index} should be updated to {expected_value}"

#------------------------------------------------------------------------------------------------------------------------------------------

def test_enum_combo(test_obj, mocker):

    expected_value = Color.GREEN
    expected_enum_index = list(Color).index(expected_value)

    # Mock imgui methods
    mocker.patch('mylib.imgui_helper.imgui.set_next_item_width')
    combo_mock = mocker.patch('mylib.imgui_helper.imgui.combo', return_value=(True, expected_enum_index))
    
    # Run the test
    ih.enum_combo('Choose Color', test_obj, 'color')
    assert test_obj.color == expected_value, "The color should update to GREEN"

    # Optionally, you can assert that the combo was called correctly
    combo_mock.assert_called_once_with('Choose Color', 0, ['RED', 'GREEN', 'BLUE'])

#------------------------------------------------------------------------------------------------------------------------------------------

def test_enum_combo_with_list(test_obj, mocker):

    expected_value = Color.GREEN
    expected_enum_index = list(Color).index(expected_value)

    # Mock the combo function to simulate user selecting the second option in an indexed attribute
    mocked_combo = mocker.patch('mylib.imgui_helper.imgui.combo', return_value=(True, expected_enum_index))
    
    # Run the test
    test_index = 1
    ih.enum_combo('Choose Color', test_obj, 'color_values', index=test_index)
    assert test_obj.color_values[test_index] == expected_value, f"The color should update to GREEN at index {test_index}"

    # Optionally, assert that the combo was called correctly with indexed handling
    mocked_combo.assert_called_once_with('Choose Color', 0, ['RED', 'GREEN', 'BLUE'])

#------------------------------------------------------------------------------------------------------------------------------------------

def test_input_text(test_obj, mocker):

    new_text = "updated text"

    # Mock the imgui.input_text function to simulate user input
    mocker.patch('mylib.imgui_helper.imgui.input_text', return_value=(True, new_text))
    
    # Invoke the input_text function
    ih.input_text("String Input", test_obj, "text", buffer_size=256)
    
    # Assert the text was updated correctly
    assert test_obj.text == new_text, f"The text attribute should be updated to '{new_text}'"

#------------------------------------------------------------------------------------------------------------------------------------------

def test_input_int(test_obj, mocker):
    
    new_value = 20  # New value after interaction

    # Mock the imgui.input_int function to simulate user input
    mocker.patch('mylib.imgui_helper.imgui.input_int', return_value=(True, new_value))
    
    # Invoke the input_int function
    ih.input_int("Integer Input", test_obj, "int_attr", step=1, step_fast=10)
    
    # Assert the integer attribute was updated correctly
    assert test_obj.int_attr == new_value, f"The int_attr should be updated to {new_value}"
