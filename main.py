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
import moderngl
import glfw
import os
import imgui
from imgui.integrations.glfw import GlfwRenderer

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


    def load_render_config(self):
        """
        Loads or initializes the application's render configuration.
        """
        app_config_manager = ConfigFileManager(self.app_name, self.app_author, 'params.pkl')
        params = app_config_manager.load_config() or PlasmaFractalParams(use_defaults=True)

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

        return window, app_config_manager


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
        imgui.begin("Control Panel")
        plasma_fractal_gui.handle_imgui_controls(self.params)
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
        logging.error(f"Unhandled exception occurred: {e}", exc_info=True)
        raise
