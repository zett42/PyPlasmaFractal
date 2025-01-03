import pytest
from PyPlasmaFractal.mylib.gfx.animation_timer import AnimationTimer

class MockTime:
    def __init__(self):
        self.current_time = 0.0
    
    def __call__(self):
        return self.current_time
    
    def advance(self, delta):
        self.current_time += delta
        return self.current_time


@pytest.fixture
def mock_time(monkeypatch):
    mock = MockTime()
    monkeypatch.setattr('time.perf_counter', mock)
    return mock


def test_init():
    
    timer = AnimationTimer()
    assert timer.accumulated_time == 0.0
    assert timer.speed == 1.0
    assert not timer.paused
    assert timer.parent is None


def test_init_with_parent():
    
    parent = AnimationTimer()
    child = AnimationTimer(parent)
    assert child.parent == parent
    assert child.get_effective_speed() == 1.0


def test_update(mock_time):
    
    timer = AnimationTimer()
    mock_time.advance(0.1)  # Advance time by 0.1 seconds
    new_time = timer.update()
    assert new_time == 0.1
    assert timer.accumulated_time == 0.1


def test_speed_control(mock_time):
    
    timer = AnimationTimer()
    timer.speed = 2.0
    assert timer.speed == 2.0
    mock_time.advance(0.1)
    fast_time = timer.update()
    
    timer.reset()
    timer.speed = 0.5
    mock_time.advance(0.1)
    slow_time = timer.update()
    
    assert fast_time == 0.2  # 0.1 * 2.0
    assert slow_time == 0.05  # 0.1 * 0.5


def test_negative_speed():
    
    timer = AnimationTimer()
    with pytest.raises(ValueError):
        timer.speed = -1.0


def test_pause_control(mock_time):
    
    timer = AnimationTimer()
    timer.paused = True
    mock_time.advance(0.1)
    paused_time = timer.update()
    assert paused_time == 0.0
    
    timer.paused = False
    mock_time.advance(0.1)
    running_time = timer.update()
    assert running_time == 0.1


def test_hierarchical_timing():
    
    parent = AnimationTimer()
    child = AnimationTimer(parent)
    
    parent.speed = 2.0
    child.speed = 3.0
    assert child.get_effective_speed() == 6.0
    
    parent.paused = True
    assert child.get_effective_speed() == 0.0
    assert child.paused  # Child should report as paused when parent is paused


def test_reset(mock_time):
    
    timer = AnimationTimer()
    mock_time.advance(0.1)
    timer.update()
    assert timer.accumulated_time == 0.1
    
    timer.reset()
    assert timer.accumulated_time == 0.0


def test_value_property(mock_time):
    
    timer = AnimationTimer()
    mock_time.advance(0.1)
    timer.update()
    assert timer.value == 0.1


def test_speed_adjustment_continuity(mock_time):
    
    timer = AnimationTimer()
    
    # Accumulate some time at normal speed
    mock_time.advance(0.1)
    timer.update()
    initial_time = timer.accumulated_time
    assert initial_time == pytest.approx(0.1)
    
    # Change speed and verify accumulated_time hasn't changed
    timer.speed = 2.0
    assert timer.accumulated_time == pytest.approx(initial_time)
    
    # Accumulate more time at new speed
    mock_time.advance(0.1)
    timer.update()
    assert timer.accumulated_time == pytest.approx(0.3)  # 0.1 (initial) + (0.1 * 2.0)


def test_nested_speed_adjustment_continuity(mock_time):
    
    parent = AnimationTimer()
    child = AnimationTimer(parent)
    
    # Accumulate time with initial speeds (both 1.0)
    mock_time.advance(0.1)
    child.update()
    initial_time = child.accumulated_time
    assert initial_time == pytest.approx(0.1)
    
    # Change parent speed and verify child time continuity
    parent.speed = 2.0
    assert child.accumulated_time == pytest.approx(initial_time)
    
    # Change child speed and verify time continuity
    child.speed = 3.0
    assert child.accumulated_time == pytest.approx(initial_time)
    
    # Accumulate more time with new combined speed (2.0 * 3.0 = 6.0)
    mock_time.advance(0.1)
    child.update()
    assert child.accumulated_time == pytest.approx(0.7)  # 0.1 + (0.1 * 6.0)


def test_step_mode_basic():
    timer = AnimationTimer()
    assert not timer.step_mode  # Default should be False
    
    timer.step_mode = True
    assert timer.step_mode
    
    # Normal update should not change time in step mode
    initial_time = timer.accumulated_time
    timer.update()
    assert timer.accumulated_time == initial_time
    
    # Step should advance time by specified amount
    timer.step(0.1)
    assert timer.accumulated_time == pytest.approx(0.1)


def test_step_mode_with_speed():
    timer = AnimationTimer()
    timer.step_mode = True
    timer.speed = 2.0
    
    timer.step(0.1)
    assert timer.accumulated_time == pytest.approx(0.2)  # 0.1 * 2.0


def test_step_mode_hierarchical():
    parent = AnimationTimer()
    child = AnimationTimer(parent)
    
    # Setting step mode on parent should propagate to child
    parent.step_mode = True
    assert child.step_mode
    
    # Set speeds for testing hierarchy
    parent.speed = 2.0
    child.speed = 3.0
    
    # Step should respect speed hierarchy
    parent.step(0.1)
    assert parent.accumulated_time == pytest.approx(0.2)  # 0.1 * 2.0
    assert child.accumulated_time == pytest.approx(0.6)   # 0.1 * 2.0 * 3.0


def test_step_mode_pause_interaction():
    timer = AnimationTimer()
    timer.step_mode = True
    timer.paused = True
    
    # Step should not advance time when paused
    timer.step(0.1)
    assert timer.accumulated_time == 0.0
    
    # Resume and verify step works
    timer.paused = False
    timer.step(0.1)
    assert timer.accumulated_time == pytest.approx(0.1)
