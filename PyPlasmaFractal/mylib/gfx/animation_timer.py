import time

class AnimationTimer:
    """
    Class to track animation time, allowing for pausing, resetting, and speed adjustments.
    Can be linked to a parent timer to create hierarchical timing relationships.
    
    Attributes:
        accumulated_time (float): The total time accumulated since the last reset.
        parent (AnimationTimer): Optional parent timer that this timer depends on.
        last_time (float): The last recorded time from the system's high-resolution clock.
        _speed (float): The current speed multiplier for time accumulation.
    """

    def __init__(self, parent: 'AnimationTimer' = None) -> None:
        """
        Initializes the animation timer.

        Args:
            parent (AnimationTimer, optional): Parent timer that this timer depends on.
                                             When provided, this timer inherits pause state from parent.
        """
        self.accumulated_time = 0.0
        self.last_time = time.perf_counter()
        self._speed = 1.0
        self._paused = False
        self.parent = parent


    def update(self, paused: bool = None, speed: float = None) -> float:
        """
        Updates the accumulated time based on elapsed time and current settings.
        The effective speed is the product of all speeds in the timer hierarchy.

        Parameters:
            paused (bool, optional): If provided, pauses or unpauses the time accumulation.
            speed (float, optional): If provided, sets a new speed for time accumulation.

        Returns:
            float: The new accumulated time.
        """
        if paused is not None:
            self.paused = paused
        if speed is not None:
            self.speed = speed

        # Consider pause state of entire timer hierarchy
        if self.paused:
            return self.accumulated_time

        current = time.perf_counter()
        delta_time = current - self.last_time
        self.accumulated_time += delta_time * self.get_effective_speed()
        self.last_time = current
        
        return self.accumulated_time


    def get_effective_speed(self) -> float:
        """
        Calculates the effective speed by multiplying speeds up the entire timer hierarchy.
        
        Returns:
            float: The product of all speeds in the timer chain.
        """
        speed = self._speed
        current = self.parent
        while current and not current.paused:
            speed *= current._speed
            current = current.parent
        return speed if not current else 0.0  # Return 0 if any parent is paused


    @property
    def value(self) -> float:
        """Returns the current accumulated time."""
        return self.accumulated_time


    @property
    def speed(self) -> float:
        """Returns this timer's speed multiplier (not including parent's speed)."""
        return self._speed


    @speed.setter
    def speed(self, new_speed: float) -> None:
        """
        Sets the speed of time accumulation.
        Note: Effective speed will be parent.speed * new_speed if timer has a parent.

        Parameters:
            new_speed (float): The new speed multiplier, must be non-negative.

        Raises:
            ValueError: If the new speed is negative.
        """
        if new_speed < 0:
            raise ValueError("Speed cannot be negative")
        self._speed = new_speed


    @property
    def paused(self) -> bool:
        """Returns whether this timer or any parent timer is paused."""
        current = self
        while current:
            if current._paused:
                return True
            current = current.parent
        return False


    @paused.setter
    def paused(self, pause: bool) -> None:
        """
        Pauses or unpauses the time accumulation.
        Note: Timer can still be effectively paused if parent timer is paused.

        Parameters:
            pause (bool): True to pause the timer, False to unpause it.
        """
        if self._paused != pause:
            self._paused = pause
            if not pause and not (self.parent and self.parent.paused):
                # Only reset last_time if we're truly unpausing (parent isn't paused)
                self.last_time = time.perf_counter()


    def reset(self) -> None:
        """Resets the accumulated time to zero and updates the last recorded time to the current time."""
        self.accumulated_time = 0.0
        self.last_time = time.perf_counter()
