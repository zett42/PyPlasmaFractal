import time

class FpsCalculator:
    def __init__(self, smoothing: float = 0.1) -> None:
        """
        Initializes the FPS calculator with a specified smoothing factor and sets up the timer.

        Args:
        smoothing (float): Smoothing factor for the exponential moving average calculation.
                           It should be between 0 and 1. A smaller value smoothens more but reacts slower.
        """
        self.ema_fps = 0.0
        self.smoothing = smoothing
        self.is_first_frame = True
        self.last_time = time.perf_counter()

    def update(self) -> None:
        """
        Update the FPS based on the elapsed time since the last frame using an internal high-resolution timer.
        """
        current_time = time.perf_counter()
        time_elapsed = current_time - self.last_time
        self.last_time = current_time
        
        if time_elapsed <= 0:
            return  # To prevent nonsensical updates
        
        current_fps = 1.0 / time_elapsed
        
        if self.is_first_frame:
            self.ema_fps = current_fps
            self.is_first_frame = False
        else:
            self.ema_fps = (current_fps * self.smoothing) + (self.ema_fps * (1 - self.smoothing))

    def get_fps(self) -> float:
        """
        Get the current smoothed FPS value.
        
        Returns:
        float: The current smoothed FPS.
        """
        return self.ema_fps
