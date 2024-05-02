import time

class AnimationTimer:
    """
    Class to track animation time, allowing for pausing, resetting, and speed adjustments.
    
    Attributes:
        accumulated_time (float): The total time accumulated since the last reset, accounting for pauses and speed changes.
        last_time (float): The last recorded time from the system's high-resolution clock.
        _speed (float): The current speed multiplier for time accumulation.
        _paused (bool): Indicates whether time accumulation is paused.
    """

    def __init__(self):
        """
        Initializes the animation timer with zero accumulated time, sets the last recorded time to the current time,
        and initializes with a speed multiplier of 1.0 and not paused.
        """
        self.accumulated_time = 0.0
        self.last_time = time.perf_counter()
        self._speed = 1.0
        self._paused = False

    def update(self, paused: bool = None, speed: float = None):
        """
        Updates the accumulated time by calculating the time elapsed since the last update,
        optionally adjusting the speed and pausing or unpausing the time accumulation.

        Parameters:
            paused (bool, optional): If provided, pauses or unpauses the time accumulation. This directly
                                    sets the internal paused state of the timer. The timer must be unpaused
                                    (if previously paused) to update the accumulated time.
            speed (float, optional): If provided, sets a new speed for time accumulation.

        Returns:
            float: The new accumulated time.
        """
        if paused is not None:
            self.paused = paused
        if speed is not None:
            self.speed = speed

        if not self._paused:
            current = time.perf_counter()
            delta_time = current - self.last_time
            self.accumulated_time += delta_time * self._speed
            self.last_time = current
        
        return self.accumulated_time

    @property
    def value(self):
        """Returns the current accumulated time."""
        return self.accumulated_time

    @property
    def speed(self):
        """Returns the current speed multiplier."""
        return self._speed

    @speed.setter
    def speed(self, new_speed):
        """
        Sets the speed of time accumulation.

        Parameters:
            new_speed (float): The new speed multiplier, must be non-negative.

        Raises:
            ValueError: If the new speed is negative.
        """
        if new_speed < 0:
            raise ValueError("Speed cannot be negative")
        self._speed = new_speed

    @property
    def paused(self):
        """Returns whether the timer is currently paused."""
        return self._paused

    @paused.setter
    def paused(self, pause):
        """
        Pauses or unpauses the time accumulation.

        Parameters:
            pause (bool): True to pause the timer, False to unpause it.
        """
        if self._paused != pause:
            self._paused = pause
            if not pause:
                # Reset the last time when resuming to avoid jumps in accumulated time
                self.last_time = time.perf_counter()

    def reset(self):
        """Resets the accumulated time to zero and updates the last recorded time to the current time."""
        self.accumulated_time = 0.0
        self.last_time = time.perf_counter()
