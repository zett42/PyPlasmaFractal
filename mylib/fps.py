# mylib/fps.py

from time import perf_counter

class FpsCalculator:
    def __init__(self, smoothing_factor=10):
        self.fps_smoothing_factor = 2 / (smoothing_factor + 1)
        self.average_fps = 0.0
        self.last_time = perf_counter()
        self.frame_count = 0

    def update(self):
        current_time = perf_counter()
        frame_time = current_time - self.last_time
        self.last_time = current_time

        current_fps = 1.0 / frame_time if frame_time > 0 else 0
        self.average_fps = (current_fps * self.fps_smoothing_factor) + (self.average_fps * (1 - self.fps_smoothing_factor))
        self.frame_count += 1

    def get_fps(self):
        return self.average_fps if self.frame_count > 1 else 0
