import time

class FrameRateLimiter:
    
    def __init__(self, fps: float = 60.0) -> None:
        """Initialize the FrameRateLimiter with a specific FPS (frames per second)."""
        self.fps = fps
        self.step_time = 1.0 / self.fps
        self.start_time = 0.0

    def start_frame(self) -> None:
        """Record the start time of a frame."""
        self.start_time = time.perf_counter()

    def end_frame(self) -> None:
        """Ensure that the current frame lasts at least the time specified by step_time."""
        # Busy wait loop to ensure frame lasts for 'step_time'
        while time.perf_counter() < (self.start_time + self.step_time):
            pass