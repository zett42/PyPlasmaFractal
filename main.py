"""
This Python script, implemented using ModernGL, GLFW, and ImGui, creates a real-time application for rendering and exploring fractal noise with 
interactive controls. The application focuses on the dynamic generation and manipulation of fractals through the use of fractal noise techniques 
for both initial generation and feedback transformations.

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

import logging
import time
import moderngl
import glfw
import os
import imgui
from imgui.integrations.glfw import GlfwRenderer

from mylib.format_exception import format_exception_ansi_colors
from mylib.texture_renderer import TextureRenderer
from mylib.feedback_texture import FeedbackTextureManager
from mylib.window_config_manager import WindowConfigManager
from mylib.animation_timer import AnimationTimer
from mylib.config_file_manager import ConfigFileManager

from plasma_fractal_renderer import PlasmaFractalRenderer
from plasma_fractal_params import PlasmaFractalParams
import plasma_fractal_gui

#---------------------------------------------------------------------------------------------------------------------------------------------

class PyPlasmaFractalApp:

    def __init__(self):
        """
        Initializes logging and sets basic application constants.
        """
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

        self.app_name = 'PyPlasmaFractal'
        self.app_author = 'zett42'

        self.last_resize_time = 0
        self.resize_requested = False
        self.resize_delay = 0.25  # Delay in seconds before applying resize changes

        self.last_click_time = 0
        self.is_fullscreen = False

        self.ui_state = {}

    def run(self):
        """
        Main entry point of the application which orchestrates the initialization,
        main loop execution, and finalization.
        """
        logging.debug('App started.')

        render_config_manager, self.params = self.load_render_config()

        self.window, self.window_config_manager = self.initialize_glfw()
        
        self.ctx, self.feedback_manager = self.create_context_and_feedback_manager(self.window)
        
        self.im_gui_renderer = self.setup_imgui(self.window)
        
        self.main_loop()
        
        self.finalize_glfw()
        
        render_config_manager.save_config(self.params)


    def main_loop(self):
        """
        Main rendering loop that continuously updates and displays the fractal visuals.
        """
        main_renderer = PlasmaFractalRenderer(self.ctx)
        texture_to_screen = TextureRenderer(self.ctx)
        timer = AnimationTimer()

        while not glfw.window_should_close(self.window):

            glfw.poll_events()

            self.handle_window_resize()
            if not self.is_fullscreen:
                self.windowed_size_pos = (*glfw.get_window_size(self.window), *glfw.get_window_pos(self.window))

            self.im_gui_renderer.process_inputs()
            imgui.new_frame()
            self.handle_gui()

            elapsed_time = timer.update(self.params.paused, self.params.speed)

            main_renderer.update_params(self.params, self.feedback_manager.previous_texture, elapsed_time)

            self.feedback_manager.render_to_texture(main_renderer.current_vao)

            texture_to_screen.render(self.feedback_manager.current_texture)

            imgui.render()
            self.im_gui_renderer.render(imgui.get_draw_data())

            glfw.swap_buffers(self.window)


    def handle_window_resize(self):
        """
        This method checks if a resize is needed and if the debounce period has passed. If both conditions are met,
        it calls the `handle_resize` method with the window, pending width, and pending height as arguments.
        """

        if self.resize_requested:
    
            if time.time() - self.last_resize_time >= self.resize_delay:
              
                logging.info(f"Handling window resize to {self.pending_width}x{self.pending_height}")

                self.ctx.viewport = (0, 0, self.pending_width, self.pending_height)
                self.feedback_manager.resize(self.pending_width, self.pending_height)
                
                self.resize_requested = False


    def load_render_config(self):
        """
        Loads or initializes the application's render configuration.
        """
        app_config_manager = ConfigFileManager(self.app_name, self.app_author, filename='fractal_config.json', model_class=PlasmaFractalParams)
        params = app_config_manager.load_config_or_default()

        logging.debug("PlasmaFractalParams:\n" + '\n'.join(f"{key}={value}" for key, value in vars(params).items()))

        return app_config_manager, params


    def initialize_glfw(self):
        """
        Initializes GLFW for window and context management, loading configurations from WindowConfigManager.
        """
        if not glfw.init():
            raise Exception("Failed to initialize GLFW")
        
        app_config_manager = WindowConfigManager(self.app_name, self.app_author)

        width, height, pos_x, pos_y = app_config_manager.get_config()

        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, glfw.TRUE)
        glfw.window_hint(glfw.RESIZABLE, glfw.TRUE)

        window = glfw.create_window(width, height, self.app_name, None, None)
        if not window:
            glfw.terminate()
            raise Exception("Failed to create GLFW window")

        glfw.make_context_current(window)
        glfw.set_window_pos(window, pos_x, pos_y)

        # Store initial window dimensions and position for toggling fullscreen
        self.windowed_size_pos = (width, height, pos_x, pos_y)

        # Set up callbacks
        glfw.set_framebuffer_size_callback(window, self.framebuffer_size_callback)
        glfw.set_mouse_button_callback(window, self.mouse_button_callback)

        return window, app_config_manager


    def framebuffer_size_callback(self, window, width, height):
        """
        Mark that a resize has been requested and store the new dimensions.
        """
        self.resize_requested = True
        self.pending_width = width
        self.pending_height = height
        self.last_resize_time = time.time()


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


    def mouse_button_callback(self, window, button, action, mods):
        """
        Handles mouse button events to detect double-clicks and toggle fullscreen.
        """
        io = imgui.get_io()
        if not io.want_capture_mouse:
            if button == glfw.MOUSE_BUTTON_LEFT and action == glfw.PRESS:
                # Check for double click (within 0.4 seconds)
                current_time = time.time()
                if current_time - self.last_click_time < 0.4:
                    self.toggle_fullscreen()

                self.last_click_time = current_time


    def create_context_and_feedback_manager(self, window):
        """
        Creates and configures the ModernGL context and associated feedback texture manager.
        """
        ctx = moderngl.create_context()

        window_width, window_height = glfw.get_framebuffer_size(window)

        feedback_manager = FeedbackTextureManager(ctx, width=window_width, height=window_height, dtype='f4', filter_x=moderngl.LINEAR, filter_y=moderngl.LINEAR, repeat_x=True, repeat_y=True)

        return ctx, feedback_manager


    def finalize_glfw(self):
        """
        Cleans up GLFW resources and saves the window configuration before exiting.
        """
        width, height = glfw.get_framebuffer_size(self.window)
        pos_x, pos_y = glfw.get_window_pos(self.window)

        self.window_config_manager.save_config(width, height, pos_x, pos_y)

        glfw.terminate()


    def handle_gui(self):
        """
        Handles the rendering and logic of the GUI elements with ImGui.
        """
        if not self.is_fullscreen:
            imgui.begin("Control Panel")
            plasma_fractal_gui.handle_imgui_controls(self.params, self.ui_state)
            imgui.end()


    def setup_imgui(self, window):
        """
        Initializes and configures ImGui with GLFW.
        """
        imgui.create_context()

        renderer = GlfwRenderer(window)

        # Replace default font with custom font
        fonts = imgui.get_io().fonts
        fonts.clear()
        fontPath = os.path.join(os.path.dirname(__file__), 'fonts/Roboto-Regular.ttf')
        fonts.add_font_from_file_ttf(fontPath, 20)
        renderer.refresh_font_texture()

        return renderer


if __name__ == "__main__":
    
    try:
        app = PyPlasmaFractalApp()  
        app.run()
    except Exception as e:
        logging.error(f"Unhandled exception occurred:\n{format_exception_ansi_colors(e)}")
        raise
