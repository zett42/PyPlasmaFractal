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

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

MY_APP_NAME = 'PyPlasmaFractal'
MY_APP_AUTHOR = 'zett42'

#---------------------------------------------------------------------------------------------------------------------------------------------

def main():
    """
    Main function to initialize the environment, create the necessary objects,
    and start the main rendering loop.
    """
    logging.debug('App started.')

    render_config_manager, params = load_render_config()

    window, window_config_manager = initialize_glfw()
    if window is None:
        return

    ctx = moderngl.create_context()

    im_gui_renderer = setup_imgui(window)

    main_loop(window, ctx, im_gui_renderer, params)

    finalize_glfw(window, window_config_manager)

    render_config_manager.save_config(params, 'params.pkl')

#---------------------------------------------------------------------------------------------------------------------------------------------

def main_loop(window, ctx, im_gui_renderer, params: PlasmaFractalParams):
    """
    Render loop that maintains the application's state, updates and renders
    the scene, handles GUI interactions.
    
    Parameters:
    - window: GLFW window object.
    - ctx: ModernGL context for rendering.
    - im_gui_renderer: ImGui GLFW renderer instance.
    """

    main_renderer = PlasmaFractalRenderer(ctx)

    window_width, window_height = glfw.get_framebuffer_size(window)

    # Using a floating point data type (f4) for the texture values is crucial for smooth feedback effect, which typically involves very small value changes.
    feedback = FeedbackTextureManager(ctx, width=window_width, height=window_height, dtype='f4' 
                                      ,filter_x=moderngl.LINEAR, filter_y=moderngl.LINEAR, 
                                      repeat_x=True, repeat_y=True)

    texture_to_screen = TextureRenderer(ctx)
    
    timer = AnimationTimer()

    while not glfw.window_should_close(window):

        glfw.poll_events()  # Handle window events
        im_gui_renderer.process_inputs()  # Process inputs for ImGui
        imgui.new_frame()  # Start a new frame for ImGui

        handle_gui(im_gui_renderer, params)

        elapsed_time = timer.update(params.paused, params.speed)

        main_renderer.update_params(params, feedback.previous_texture, elapsed_time)

        # Let the main_renderer render to an offscreen texture
        feedback.render_to_texture(main_renderer.current_vao)

        # Copy the offscreen texture to the screen
        texture_to_screen.render(feedback.current_texture)

        # Render the ImGui elements to the screen
        imgui.render()
        im_gui_renderer.render(imgui.get_draw_data())

        # Swap buffers for smooth display update
        glfw.swap_buffers(window)  

#---------------------------------------------------------------------------------------------------------------------------------------------

def load_render_config():
    
    app_config_manager = ConfigFileManager(MY_APP_NAME, MY_APP_AUTHOR)

    params = app_config_manager.load_config('params.pkl') or PlasmaFractalParams(use_defaults=True) 
    #params = PlasmaFractalParams(use_defaults=True) 

    logging.debug("PlasmaFractalParams:\n" + '\n'.join(f"    {key}={value}" for key, value in vars(params).items()))

    return app_config_manager, params

#---------------------------------------------------------------------------------------------------------------------------------------------

def initialize_glfw():
    """
    Initializes GLFW and creates a window with an OpenGL context using configuration loaded by WindowConfigManager.
       
    Returns:
    - A tuple containing the GLFW window object and the instance of WindowConfigManager or (None, None) if initialization fails.
    """
    if not glfw.init():
        raise Exception("Failed to initialize GLFW")

    app_config_manager = WindowConfigManager(MY_APP_NAME, MY_APP_AUTHOR)
    width, height, pos_x, pos_y = app_config_manager.get_config()

    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, glfw.TRUE)

    window = glfw.create_window(width, height, MY_APP_NAME, None, None)
    if not window:
        glfw.terminate()
        raise Exception("Failed to create GLFW window")

    glfw.make_context_current(window)
    glfw.set_window_pos(window, pos_x, pos_y)

    return window, app_config_manager

#---------------------------------------------------------------------------------------------------------------------------------------------

def finalize_glfw(window, app_config_manager):
    """
    Finalizes the GLFW context by saving the window configuration and terminating GLFW.

    Parameters:
    - window: The GLFW window object.
    - app_config_manager: An instance of WindowConfigManager used to manage window configurations.
    """
    width, height = glfw.get_framebuffer_size(window)
    pos_x, pos_y = glfw.get_window_pos(window)
    app_config_manager.save_config(width, height, pos_x, pos_y)
    glfw.terminate()

#---------------------------------------------------------------------------------------------------------------------------------------------

def handle_gui(im_gui_renderer: GlfwRenderer, params: PlasmaFractalParams):
    """
    Renders the graphical user interface using ImGui and updates the GUI state.

    Parameters:
    - im_gui_renderer: ImGui renderer for GLFW.
    - params: An instance of GUIState that will be updated based on GUI interactions.
    """
    # Start a new ImGui window
    imgui.begin("Control Panel")
    
    # Create the imgui controls and update the params attributes.
    plasma_fractal_gui.handle_imgui_controls(params)
    
    # End the ImGui window
    imgui.end()

#---------------------------------------------------------------------------------------------------------------------------------------------

def setup_imgui(window):
    """
    Sets up ImGui context and integrates it with GLFW.

    Parameters:
    - window: GLFW window object.

    Returns:
    - Initialized ImGui GLFW renderer.
    """
    imgui.create_context()

    renderer = GlfwRenderer(window)

    fonts = imgui.get_io().fonts
    fonts.clear()  # to replace the default font

    fontPath = os.path.join(os.path.dirname(__file__), 'fonts/Roboto-Regular.ttf')
    fonts.add_font_from_file_ttf(fontPath, 20)
    
    renderer.refresh_font_texture()

    return renderer

#---------------------------------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.error(f"Unhandled exception occurred: {e}", exc_info=True)
        raise
