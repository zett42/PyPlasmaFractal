import pytest
import numpy as np
from PyPlasmaFractal.mylib.gfx.viewer import Viewer  # Updated import path

def test_initialization():
    viewer = Viewer()
    assert np.allclose(viewer.position, (0.0, 0.0, 0.0))
    assert np.allclose(viewer.direction, (0.0, 0.0, -1.0))
    assert np.allclose(viewer.up, (0.0, 1.0, 0.0))
    assert np.allclose(viewer.right, (1.0, 0.0, 0.0))
    assert viewer.roll_angle == 0.0

def test_position_setting():
    viewer = Viewer()
    viewer.position = (1.0, 2.0, 3.0)
    assert np.allclose(viewer.position, (1.0, 2.0, 3.0))

def test_direction_setting():
    viewer = Viewer()
    viewer.direction = (1.0, 0.0, 0.0)
    assert np.allclose(viewer.direction, (1.0, 0.0, 0.0))
    assert np.allclose(viewer.up, (0.0, 1.0, 0.0))
    assert np.allclose(viewer.right, (0.0, 0.0, 1.0))  # Correct expected right vector

def test_invalid_direction():
    viewer = Viewer()
    with pytest.raises(ValueError):
        viewer.direction = (0.0, 0.0, 0.0)

def test_move_forward():
    viewer = Viewer()
    viewer.move_forward(5.0)
    assert np.allclose(viewer.position, (0.0, 0.0, -5.0))

def test_move_right():
    viewer = Viewer()
    viewer.move_right(5.0)
    assert np.allclose(viewer.position, (5.0, 0.0, 0.0))

def test_move_up():
    viewer = Viewer()
    viewer.move_up(5.0)
    assert np.allclose(viewer.position, (0.0, 5.0, 0.0))

def test_pitch():
    viewer = Viewer()
    viewer.pitch(np.pi / 2)
    assert np.allclose(viewer.direction, (0.0, 1.0, 0.0))
    assert np.allclose(viewer.up, (1.0, 0.0, 0.0))
    assert np.allclose(viewer.right, (0.0, 0.0, -1.0))

def test_yaw():
    viewer = Viewer()
    viewer.yaw(np.pi / 2)
    assert np.allclose(viewer.direction, (1.0, 0.0, 0.0))  # Expected direction after yaw to the right
    assert np.allclose(viewer.right, (0.0, 0.0, 1.0))  # Expected right vector after yaw
    assert np.allclose(viewer.up, (0.0, 1.0, 0.0))

def test_roll():
    viewer = Viewer()
    viewer.roll(np.pi / 2)
    print(f"Right vector: {viewer.right}")
    print(f"Up vector: {viewer.up}")
    assert np.allclose(viewer.right, (0.0, 1.0, 0.0)), f"Expected (0.0, 1.0, 0.0) but got {viewer.right}"
    assert np.allclose(viewer.up, (-1.0, 0.0, 0.0)), f"Expected (-1.0, 0.0, 0.0) but got {viewer.up}"
    assert viewer.roll_angle == np.pi / 2, f"Expected roll angle to be {np.pi / 2} but got {viewer.roll_angle}"
