"""
This Python script utilizes ModernGL, GLFW, and ImGui to create a real-time application for rendering and interactively exploring fractal noise.
The application leverages fractal noise techniques for generating dynamic fractal patterns and applying feedback transformations. Feedback loops
are integral to this application, enhancing the visuals by recursively processing and layering outputs to produce complex, evolving textures that 
can appear almost organic in nature.

Key functionalities:
- Initializes a GLFW window and OpenGL context suitable for high-performance graphics rendering.
- Sets up ImGui to provide an interactive interface for real-time manipulation of fractal parameters.
- Implements a main rendering loop that continuously updates and displays the fractal visuals, incorporating user input and automated processes.
- Uses fragment shaders to generate fractal noise for initial image creation and applies similar techniques to transform the feedback, enhancing 
  the complexity and continuity of visual effects.
- Manages user settings and fractal parameters persistently, allowing for experimentation and refinement of visual outputs.

Major dependencies:
- moderngl: Facilitates OpenGL rendering.
- glfw: Manages window creation, input processing, and system interactions.
- imgui: Enables the creation and management of an interactive GUI.
"""
# Standard library and third-party imports
import logging
import os
import sys
import time
from pathlib import Path
import imgui
import moderngl
from imgui.integrations.glfw import GlfwRenderer

# Ensure the package root is in sys.path so that the local modules can be imported when PyInstaller runs the script
current_dir = Path(__file__).resolve().parent
parent_dir = current_dir.parent
sys.path.insert(0, str(parent_dir))  # Add parent directory to sys.path

# Debug print statements
print("Current directory:", current_dir)
print("Parent directory:", parent_dir)
print("sys.path:", sys.path)

# Local modules - libraries
from PyPlasmaFractal.mylib.config.config_path_manager import ConfigPathManager
from PyPlasmaFractal.mylib.config.json_file_storage import JsonFileStorage
from PyPlasmaFractal.mylib.config.storage import StorageItemNotFoundError
from PyPlasmaFractal.mylib.config.function_registry import FunctionRegistry
from PyPlasmaFractal.mylib.gfx.animation_timer import AnimationTimer
from PyPlasmaFractal.mylib.gfx.fps import FpsCalculator
from PyPlasmaFractal.mylib.gfx.frame_rate_limiter import FrameRateLimiter
from PyPlasmaFractal.mylib.gfx.fullscreen_texture_renderer import FullscreenTextureRenderer
from PyPlasmaFractal.mylib.gfx.separable_gaussian_blur import SeparableGaussianBlur
from PyPlasmaFractal.mylib.gfx.texture_render_manager import PingpongTextureRenderManager
from PyPlasmaFractal.mylib.gui.icons import Icons
from PyPlasmaFractal.mylib.gui.window_config_manager import WindowConfigManager
from PyPlasmaFractal.mylib.python_utils.format_exception import format_exception_ansi_colors
from PyPlasmaFractal.mylib.named_tuples import Size
from PyPlasmaFractal.mylib.recording.video_recorder import VideoRecorder
from PyPlasmaFractal.mylib.noise.fractal_noise_params import FractalNoiseParamsType, NoiseAlgorithmType

# Local modules - application
from PyPlasmaFractal.plasma_fractal_gui import PlasmaFractalGUI
from PyPlasmaFractal.plasma_fractal_params import PlasmaFractalParams
from PyPlasmaFractal.plasma_fractal_renderer import PlasmaFractalRenderer
from PyPlasmaFractal.plasma_fractal_resources import resource_path
from PyPlasmaFractal.plasma_fractal_types import ShaderFunctionType

glfw = None  # Global variable to store the GLFW module reference, which is imported later in the code

CONFIG_FILE_NAME = 'fractal_config.json'

#---------------------------------------------------------------------------------------------------------------------------------------------

class PyPlasmaFractalApp:

    def __init__(self):
        """
        Initializes logging and sets basic application constants.
        """
        self.setup_logging()

        self.app_name = 'PyPlasmaFractal'
        self.app_author = 'zett42'

        # Initialize variables for window management and resizing
        self.last_resize_time = 0
        self.resize_requested = False
        self.requested_framebuffer_size = Size(0, 0)
        self.resize_delay = 0.5  # Delay in seconds before applying resize changes

        # Initialize variables for double-click detection and fullscreen toggling
        self.last_click_time = 0
        self.is_fullscreen = False

        # Setup paths
        self.path_manager = ConfigPathManager(self.app_name, self.app_author, app_specific_path=resource_path(''))
        
        # Setup video recording
        self.user_videos_directory = self.path_manager.user_specific_path / 'videos'
        self.user_videos_directory.mkdir(parents=True, exist_ok=True)
        self.recorder = VideoRecorder()

        # Initialize timing-related variables
        self.timer = AnimationTimer()
        self.fps_calculator = FpsCalculator() 
        self.desired_fps = 60.0

        self.register_selectable_shader_functions()   

        # Setup GUI
        self.gui = PlasmaFractalGUI(self.path_manager, self.shader_function_registries, self.user_videos_directory, self.desired_fps) 
        
        # Initialized in run()
        self.params = None
        
        
    def setup_logging(self):

        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    
        # Ignore debug messages from this module
        logger = logging.getLogger('.mylib.shader_template_system')
        logger.setLevel(logging.INFO)        
        

    def run(self):
        """
        Main entry point of the application which orchestrates the initialization,
        main loop execution, and finalization.
        """
        logging.debug('App started.')   

        self.load_config()

        self.initialize_glfw()
        
        self.setup_render_context(self.window)
        
        self.setup_imgui(self.window)
        
        self.main_loop()

        self.finalize()       


    def load_config(self):
        """
        Loads or initializes the application's render configuration.
        """  
        
        logging.info(f'Loading configuration from {CONFIG_FILE_NAME} in directory "{self.path_manager.user_specific_path}"')

        self.params = PlasmaFractalParams(self.shader_function_registries)

        storage = JsonFileStorage(self.path_manager.user_specific_path)
        try:
            data = storage.load(CONFIG_FILE_NAME)
            self.params.merge_dict(data)
        except StorageItemNotFoundError:
            # No configuration file found, use default values
            logging.warning(f"No configuration file found. Using default values.")
        except Exception as e:
            # Handle unexpected exceptions
            logging.error(f"Failed to load configuration: {e}. Using default values.")
            self.gui.notifications.push_notification(PlasmaFractalGUI.Notification.LOAD_CONFIG_ERROR, f"Failed to load configuration: {e}")
        
        logging.debug(f"PlasmaFractalParams:\n{self.params.to_dict()}")


    def save_config(self):
        
        logging.info(f'Saving configuration to "{CONFIG_FILE_NAME}" in directory "{self.path_manager.user_specific_path}"')
        
        # TODO: exception handling
        storage = JsonFileStorage(self.path_manager.user_specific_path)
        storage.save(self.params.to_dict(), CONFIG_FILE_NAME)


    def initialize_glfw(self):
        """
        Initializes GLFW for window and context management, loading configurations from WindowConfigManager.
        """
        if getattr(sys, 'frozen', False):
            # If the application is run as a bundle, add the location of the glfw DLLs to the search path to avoid errors.
            os.add_dll_directory(str(resource_path('')))

        # Import glfw here after setting the DLL search path to avoid issues with the DLLs not being found
        global glfw
        import glfw

        if not glfw.init():
            raise Exception("Failed to initialize GLFW")
        
        self.window_config_manager = WindowConfigManager(self.app_name, self.app_author)

        width, height, pos_x, pos_y = self.window_config_manager.get_config()

        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, glfw.TRUE)
        glfw.window_hint(glfw.RESIZABLE, glfw.TRUE)

        self.window = glfw.create_window(width, height, self.app_name, None, None)
        if not self.window:
            glfw.terminate()
            raise Exception("Failed to create GLFW window")

        glfw.make_context_current(self.window)
        glfw.set_window_pos(self.window, pos_x, pos_y)

        # Store initial window dimensions and position for toggling fullscreen
        self.windowed_size_pos = (width, height, pos_x, pos_y)

        # Set up callbacks
        glfw.set_framebuffer_size_callback(self.window, self.framebuffer_size_callback)
        glfw.set_mouse_button_callback(self.window, self.mouse_button_callback)


    def framebuffer_size_callback(self, window, width, height):
        """
        Mark that a resize has been requested and store the new dimensions.
        """
        self.resize_requested = True
        self.requested_framebuffer_size = Size(width, height)
        self.last_resize_time = time.time()


    def mouse_button_callback(self, window, button, action, mods):
        """
        Handles mouse button events outside of the IMGUI window to detect double-clicks and toggle fullscreen.
        """
        io = imgui.get_io()
        if not io.want_capture_mouse:
            if button == glfw.MOUSE_BUTTON_LEFT and action == glfw.PRESS:
                # Check for double click (within 0.4 seconds)
                current_time = time.time()
                if current_time - self.last_click_time < 0.4:
                    self.toggle_fullscreen()

                self.last_click_time = current_time


    def toggle_fullscreen(self):
        """
        Toggles the window between fullscreen and windowed mode based on current state.
        """
        window = self.window 
        current_monitor = glfw.get_window_monitor(window)
        if current_monitor:
            # Currently fullscreen, switch to windowed mode
            width, height, x, y = self.windowed_size_pos
            glfw.set_window_monitor(window, None, x, y, width, height, glfw.DONT_CARE)
        else:
            # Currently windowed, switch to fullscreen
            monitor = glfw.get_primary_monitor()
            mode = glfw.get_video_mode(monitor)
            glfw.set_window_monitor(window, monitor, 0, 0, mode.size.width, mode.size.height, mode.refresh_rate)

        self.is_fullscreen = not current_monitor


    def setup_render_context(self, window):
        """
        Creates and configures the ModernGL context and associated feedback texture manager.
        """
        self.ctx = moderngl.create_context()

        width, height = glfw.get_framebuffer_size(window)

        self.feedback_manager = PingpongTextureRenderManager(self.ctx, width=width, height=height, dtype='f4', filter_x=moderngl.LINEAR, filter_y=moderngl.LINEAR) # repeat_x=True, repeat_y=True)


    def setup_imgui(self, window):
        """
        Initializes and configures ImGui with GLFW.
        """
        imgui.create_context()

        self.im_gui_renderer = GlfwRenderer(window)

        fonts_dir = resource_path('fonts')

        # Replace default font with custom font
        fonts = imgui.get_io().fonts
        fonts.clear()
        font_path = fonts_dir / 'Roboto-Regular.ttf'
        logging.debug(f"Loading font from: {font_path}")
        fonts.add_font_from_file_ttf(str(font_path), 20)

        # Merge icon font
        Icons.merge_font(fonts_dir, font_file_name='MaterialDesignIconsDesktop.ttf', font_size=28)

        # Update the font texture to apply changes
        self.im_gui_renderer.refresh_font_texture()


    def register_selectable_shader_functions(self):
        """
        Registers user-selectable shader functions.
        """
        shaders_path = resource_path('shaders')
        descriptor_filter = '*.descr.json'
        
        function_dirs = {
            ShaderFunctionType.NOISE: 'noise_functions',
            ShaderFunctionType.BLEND: 'blend_functions',
            ShaderFunctionType.WARP : 'warp_functions',
            ShaderFunctionType.COLOR : 'color_functions',
        }
        
        custom_param_types = [ NoiseAlgorithmType(), FractalNoiseParamsType() ]
        
        self.shader_function_registries = {}
        
        for func_type, dir_name in function_dirs.items():
            try:
                self.shader_function_registries[func_type] = FunctionRegistry(JsonFileStorage(shaders_path / dir_name), descriptor_filter, custom_param_types)
            except Exception as e:
                raise RuntimeError(f"Failed to register shader functions for type {func_type}: {str(e)}") from e
            
        
    def main_loop(self):
        """
        Main rendering loop that continuously updates and displays the fractal visuals.
        """
        main_renderer = PlasmaFractalRenderer(self.ctx, self.shader_function_registries)
        
        texture_to_screen = FullscreenTextureRenderer(self.ctx)
        
        # The separable Gaussian blur uses the feedback manager's textures to blur the previous frame's texture. To efficiently use resources,
        # the current frame's texture is used as intermediate storage (before the noise visuals are rendered).
        gaussian_blur = SeparableGaussianBlur(self.ctx, self.feedback_manager)
        
        fps_limiter = FrameRateLimiter(self.desired_fps)     
        
        self.first_frame = True                

        while not glfw.window_should_close(self.window):

            fps_limiter.start_frame()

            glfw.poll_events()
            self.handle_window_resize()

            self.handle_gui()

            elapsed_time = self.handle_time()

            if not self.gui.animation_paused:
                self.render_frame(main_renderer, gaussian_blur, elapsed_time)

            texture_to_screen.render(self.feedback_manager.current_texture, self.ctx.screen)

            self.handle_recording()

            imgui.render()
            self.im_gui_renderer.render(imgui.get_draw_data())

            glfw.swap_buffers(self.window)

            if not self.recorder.is_recording:
                fps_limiter.end_frame()
                
            self.fps_calculator.update()
            
            self.first_frame = False
    
    
    def render_frame(self, main_renderer: PlasmaFractalRenderer, gaussian_blur: SeparableGaussianBlur, elapsed_time: float):
        """
        Render a single frame of the fractal visuals.
        """
        # Check if the first frame is being rendered to avoid issues with uninitialized feedback textures
        if not self.first_frame:
            # Swap the textures so the previous frame will be used for feedback  
            self.feedback_manager.swap_textures()
        
            if self.params.enable_feedback_blur:
                # Apply Gaussian blur to the previous frame, utilizing the (yet unused) destination texture as intermediate storage
                gaussian_blur.apply_blur(self.params.feedback_blur_radius, self.params.feedback_blur_radius_power)
            
        # Clear the feedback textures if a new preset has been loaded, to ensure we start with a clean state
        if self.gui.notifications.pull_notification(PlasmaFractalGUI.Notification.NEW_PRESET_LOADED):
            self.feedback_manager.clear()
            self.first_frame = True

        # Update the main renderer with the current parameters and render to the destination texture
        main_renderer.update_params(self.params, self.feedback_manager.previous_texture, 
                                    self.timer.accumulated_time, self.feedback_manager.aspect_ratio)
        
        # Render the fractal to the destination texture
        self.feedback_manager.render_to_texture(main_renderer.current_vao)
        

    def handle_window_resize(self):
        """
        This method checks if a resize is needed and if the debounce period has passed. If both conditions are met,
        it calls the `handle_resize` method with the window, pending width, and pending height as arguments.
        """

        if self.resize_requested:
    
            if time.time() - self.last_resize_time >= self.resize_delay:
              
                logging.debug(f"Handling framebuffer resize to {self.requested_framebuffer_size}")

                self.ctx.viewport = (0, 0, self.requested_framebuffer_size.width, self.requested_framebuffer_size.height)

                # During recording, the feedback textures should not be resized, since the video size is fixed
                if not self.recorder.is_recording:
                    self.feedback_manager.resize(self.requested_framebuffer_size.width, self.requested_framebuffer_size.height)
                    self.first_frame = True
                
                self.resize_requested = False

        if not self.is_fullscreen:
            self.windowed_size_pos = (*glfw.get_window_size(self.window), *glfw.get_window_pos(self.window))


    def handle_gui(self):
        """
        Handles the rendering and logic of the GUI elements with ImGui.
        """
        self.im_gui_renderer.process_inputs()
        imgui.new_frame()

        # Update GUI attributes that are independent of the render params
        self.gui.actual_fps = self.fps_calculator.get_fps()
        self.gui.desired_fps = self.desired_fps

        # Render GUI elements
        self.gui.update(self.params)


    def handle_time(self) -> float:
        """Update the timer and return the current accumulated time."""
        return self.timer.update(self.gui.animation_paused, self.params.speed)


    def handle_recording(self):
        """
        Handles the recording of video frames based on the current recording state.
        """

        # If GUI recording state has changed, start or stop recording accordingly
        if (notifyData := self.gui.notifications.pull_notification(PlasmaFractalGUI.Notification.RECORDING_STATE_CHANGED)):

            logging.debug(f"Recording state changed to: {notifyData['is_recording']}")

            if notifyData['is_recording']:

                logging.debug(f"Starting recording with file name: {self.gui.recording_file_name}, size: {self.gui.recording_width}x{self.gui.recording_height}, fps: {self.gui.recording_fps}, quality: {self.gui.recording_quality}")

                # Temporarily resize feedback texture to recording size
                self.feedback_manager.resize(*self.recorder.get_aligned_dimensions(self.gui.recording_width, self.gui.recording_height))

                # During recording, the time is frame-based and starts at the current time of the timer.
                self.timer.paused = True

                video_path = self.user_videos_directory / self.gui.recording_file_name
                try:
                    self.recorder.start_recording(video_path, self.feedback_manager.width, self.feedback_manager.height, fps=self.gui.recording_fps, 
                                                  quality=self.gui.recording_quality)
                except Exception as e:
                    logging.error(f"The recording could not be started: {e}")
                    self.gui.notifications.push_notification(PlasmaFractalGUI.Notification.RECORDING_ERROR, str(e))

                # Configure timer for recording
                self.timer.step_mode = True

            else:
                logging.debug("Stopping recording")

                try:
                    self.recorder.stop_recording()
                except Exception as e:
                    logging.error(f"The recording could not be finished: {e}")
                    self.gui.notifications.push_notification(PlasmaFractalGUI.Notification.RECORDING_ERROR, str(e))

                self.gui.recording_time = 0

                # Restore feedback texture size
                width, height = glfw.get_framebuffer_size(self.window)
                self.feedback_manager.resize(width, height)

                # Restore normal timer operation
                self.timer.step_mode = False
                

        # Capture frame if recording is active
        if self.recorder.is_recording:

            # Step the timer by a fixed amount for consistent timing
            self.timer.step(1.0 / self.recorder.fps)
            try:
                self.recorder.capture_frame(self.feedback_manager.current_texture)
            except Exception as e:
                logging.error(f"Failed to capture frame: {e}")
                self.gui.notifications.push_notification(PlasmaFractalGUI.Notification.RECORDING_ERROR, str(e))

            self.gui.recording_time = self.recorder.recording_time


    def finalize(self):
        """
        Save the fractal params and release resources.
        """
        self.save_config()

        logging.info('Saving window configuration')
        width, height = glfw.get_window_size(self.window)  # Gets the client area size
        pos_x, pos_y = glfw.get_window_pos(self.window)
        self.window_config_manager.save_config(width, height, pos_x, pos_y)

        logging.info('Releasing ModernGL resources')
        self.ctx.release()

        logging.info('Terminating GLFW')
        glfw.terminate()


if __name__ == "__main__":
    
    try:
        app = PyPlasmaFractalApp()  
        app.run()
    except Exception as e:
        logging.error(f"Unhandled exception occurred:\n{format_exception_ansi_colors(e)}")
        raise
