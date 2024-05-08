import math
import time
from enum import Enum, auto

class MouseState(Enum):
    """Defines the possible states of the mouse interaction."""
    Active   = auto()  # Mouse is moving
    Inactive = auto()  # Mouse is not moving
    Idle     = auto()  # Mouse is not moving for a certain period of time

class FadeState(Enum):
    """Defines the states for window fade transitions."""
    Active    = auto()  # Window is at maximum visibility
    FadingOut = auto()  # Window is fading out
    Inactive  = auto()  # Window is at minimum visibility
    FadingIn  = auto()  # Window is fading in

class WindowFadeManager:
    """Manages the fading of a window based on mouse activity."""

    def __init__(self, 
                 fade_delay: float = 5.0, 
                 fade_out_duration: float = 1.0, fade_in_duration: float = 0.25, 
                 alpha_active: float = 1.0, alpha_inactive: float = 0.0):
        """
        Initializes a new instance of the WindowFadeManager.
        
        Parameters:
            fade_delay (int): The time in seconds the mouse must be idle before fading out starts.
            fade_out_duration (float): Duration in seconds of the fade out transition.
            fade_in_duration (float): Duration in seconds of the fade in transition.
            alpha_active (float): Alpha value when window is fully active.
            alpha_inactive (float): Alpha value when window is fully inactive.
        """
        self.last_mouse_pos = None
        self.last_time_mouse_moved = time.time()
        self.fade_delay = fade_delay
        self.fade_out_duration = fade_out_duration
        self.fade_in_duration = fade_in_duration
        self._alpha = alpha_active
        self.alpha_active = alpha_active
        self.alpha_inactive = alpha_inactive
        self.start_alpha = alpha_active  # Initial alpha for any fade operation
        self.state = FadeState.Active


    def update(self, mouse_pos: tuple[float, float], window_pos: tuple[float, float] = None, window_size: tuple[float, float] = None) -> float:
        """
        Update the fading state based on the current mouse position and time elapsed since the last update.
        
        This method manages transitions between different fading states of the window based on mouse activity:
        - Transitions to FadingOut if the mouse remains idle for the specified fade delay while the window is Active.
        - Completes the fade-in process and transitions to Active if the current state is FadingIn and the conditions are met.
        - Initiates or reverses the fading process based on mouse activity when in FadingOut or Inactive states.
        
        Parameters:
            mouse_pos (tuple[float, float]): The current position of the mouse, used to determine activity.
            window_pos (tuple[float, float], optional): The position of the window. If not provided, the current window position is used.
            window_size (tuple[float, float], optional): The size of the window. If not provided, the current window size is used.

        Returns:
            float: The current alpha value of the window, ranging from 0.0 to 1.0.
        """
        current_time = time.time()
        
        mouse_state = self.get_mouse_state(current_time, mouse_pos, window_pos, window_size)

        if self.state == FadeState.Active and mouse_state == MouseState.Idle:
            self.state = FadeState.FadingOut
            self.start_time = current_time
            self.start_alpha = self._alpha

        elif self.state == FadeState.FadingIn:
            if self.process_fade(current_time, self.start_alpha, self.alpha_active, self.start_time, self.fade_in_duration):
                self.state = FadeState.Active

        elif self.state == FadeState.FadingOut:
            if mouse_state == MouseState.Active:
                self.state = FadeState.FadingIn
                self.start_alpha = self._alpha
                self.start_time = current_time
            elif self.process_fade(current_time, self.start_alpha, self.alpha_inactive, self.start_time, self.fade_out_duration):
                self.state = FadeState.Inactive

        elif self.state == FadeState.Inactive and mouse_state == MouseState.Active:
            self.state = FadeState.FadingIn
            self.start_alpha = self.alpha_inactive
            self.start_time = current_time

        return self.alpha


    def get_mouse_state(self, current_time: float, 
                        mouse_pos: tuple[float, float], 
                        window_pos: tuple[float, float] = None, 
                        window_size: tuple[float, float] = None) -> MouseState:
        """
        Determine the mouse state based on its position, last movement time, and window rect.

        Parameters:
        current_time (float): The current time as a float timestamp.
        mouse_pos (tuple[float, float]): The current position of the mouse.
        window_pos (tuple[float, float]): The position (x, y) of the top-left corner of the window.
        window_size (tuple[float, float]): The size (width, height) of the window.

        Returns:
        MouseState: The current state of the mouse (Active, Inactive, Idle).
        """
        if window_pos is not None and window_size is not None:
            window_rect = (window_pos[0], window_pos[1], window_pos[0] + window_size[0], window_pos[1] + window_size[1])
            if window_rect[0] <= mouse_pos[0] <= window_rect[2] and \
               window_rect[1] <= mouse_pos[1] <= window_rect[3]:
                return MouseState.Active
        
        if mouse_pos != self.last_mouse_pos:
            self.last_mouse_pos = mouse_pos
            self.last_time_mouse_moved = current_time
            return MouseState.Active
        elif current_time - self.last_time_mouse_moved >= self.fade_delay:
            return MouseState.Idle
        else:
            return MouseState.Inactive


    def process_fade(self, current_time: float, start_alpha: float, end_alpha: float, start_time: float, duration: float) -> bool:
        """Process the fading transition over the specified duration.

        Parameters:
            current_time (float): Current timestamp.
            start_alpha (float): Starting alpha value for the fade.
            end_alpha (float): Ending alpha value for the fade.
            start_time (float): Start timestamp for the fade transition.
            duration (float): Total duration of the fade.

        Returns:
            bool: True if the fade is complete, otherwise False.
        """
        elapsed_time = current_time - start_time
        if elapsed_time >= duration:
            self._alpha = end_alpha
            return True
        else:
            # Calculate smooth transition based on time elapsed
            progress = self._ease_in_out_cubic( elapsed_time / duration )             
            self._alpha = start_alpha + (end_alpha - start_alpha) * progress
            return False

    @staticmethod    
    def _ease_in_out_cubic(t):
        """
        Ease in/out function using a cubic polynomial formula.
        It calculates the position at a given time `t` where `t` is normalized (0.0 to 1.0).

        Parameters:
        - t (float): Normalized time from 0.0 to 1.0.

        Returns:
        - float: Calculated position based on ease in/out cubic formula.
        """
        return 3 * t**2 - 2 * t**3      

    @property
    def alpha(self):
        """Gets the current alpha value, ensuring it remains within valid bounds."""
        return max(0.0, min(1.0, self._alpha))
