import logging
from typing import *
import moderngl
import numpy as np
from collections import namedtuple

from PyPlasmaFractal.mylib.config.dict_text_storage import DictTextFileStorage
from PyPlasmaFractal.mylib.config.function_glsl_generator import GlslGenerator
from PyPlasmaFractal.mylib.config.function_registry import FunctionInfo, FunctionRegistry
from PyPlasmaFractal.mylib.named_tuples import Vec2
from PyPlasmaFractal.plasma_fractal_resources import resource_path
from PyPlasmaFractal.mylib.gfx.shader_cache import VariantShaderCache
from PyPlasmaFractal.plasma_fractal_types import ShaderFunctionType
from PyPlasmaFractal.plasma_fractal_params import PlasmaFractalParams


class PlasmaFractalRenderer:
    """
    Handles the rendering process.
    
    Attributes:
        ctx (moderngl.Context): The OpenGL context.
        vbo (moderngl.Buffer): Vertex buffer object storing vertices for a full screen quad.
        vao (moderngl.VertexArray): Vertex array object that defines buffer layouts and shader inputs.
        params (Dict[str, Any]): Configuration dictionary for rendering options.
        shader_cache (VariantShaderCache): Caches and manages shader variants.
    """
    def __init__(self, ctx: moderngl.Context, shader_function_registries: Dict[ShaderFunctionType, FunctionRegistry] ):
        """
        Initializes a new instance of the PlasmaFractalRenderer class.

        Args:
            ctx (moderngl.Context): The OpenGL context.

        Returns:
            None
        """
        self.ctx = ctx

        self.vbo = self._create_fullscreen_quad()
        self.program = None
        self.vao = None

        self.scale = Vec2( 1.0, 1.0 )
        self.warp_scale = Vec2( 1.0, 1.0 )

        # Get the shaders directory relative to the current script's directory
        shader_base_directory = resource_path('shaders')

        # Load the shader sources into a dictionary to avoid repeated file system access, when a different shader variant is choosen
        shader_storage = DictTextFileStorage(shader_base_directory, '*.glsl')

        # Provide the shader sources to the cache.
        self.shader_cache = VariantShaderCache(ctx, 'vertex_shader.glsl', 'fragment_shader.glsl', shader_storage)
        
        self.noise_function_registry = shader_function_registries[ShaderFunctionType.NOISE]
        self.blend_function_registry = shader_function_registries[ShaderFunctionType.BLEND]
        self.warp_function_registry  = shader_function_registries[ShaderFunctionType.WARP]        
        self.color_function_registry = shader_function_registries[ShaderFunctionType.COLOR]


    def _create_fullscreen_quad(self) -> moderngl.Buffer:
        """
        Creates a VBO (Vertex Buffer Object) for a fullscreen quad (two triangles),
        covering the viewport.

        Returns:
            moderngl.Buffer: The created VBO for the fullscreen quad.
        """
        vertices = np.array([
            -1.0, -1.0,   # Bottom-left
             1.0, -1.0,   # Bottom-right
            -1.0,  1.0,   # Top-left
             1.0, -1.0,   # Bottom-right (repeated)
             1.0,  1.0,   # Top-right
            -1.0,  1.0,   # Top-left (repeated)
        ], dtype='f4')

        return self.ctx.buffer(vertices.tobytes())


    def update_params(self, 
                      params: PlasmaFractalParams,
                      feedback_texture: moderngl.Texture, 
                      noise_time: float,
                      warp_time: float, 
                      aspect_ratio: float):
        """
        Applies the rendering parameters to generate the final shader programs from templates and configures them.

        Args:
            params (PlasmaFractalParams): The parameters for the plasma fractal rendering.
            feedback_texture (moderngl.Texture): The feedback texture used for the feedback effect.
            noise_time (float): The current time for main noise.
            warp_time (float): The current time for warp noise.
            aspect_ratio (float): The aspect ratio of the viewport.
        """
        #logging.debug("Updating params:" + '\n'.join(f"    {key}={value}" for key, value in vars(params).items()))

        if aspect_ratio > 1.0:
            view_scale = Vec2(aspect_ratio, 1.0)
        else:
            view_scale = Vec2(1.0, 1.0 / aspect_ratio)  
       
        noise_function_info = self.noise_function_registry.get_function_info(params.noise.noise_algorithm)

        # Parameters that define how the fragment shader is generated from templates
        fragment_template_params = {
            'NOISE_FUNC': params.noise.noise_algorithm,
            'NOISE_MIN': noise_function_info.min_value,
            'NOISE_MAX': noise_function_info.max_value,
            'FB_ENABLED': 'enabled' if params.enable_feedback else 'disabled',
            'FB_BLEND_FUNC': params.feedback_function,
            'FB_BLEND_FUNC_UNIFORMS': GlslGenerator.generate_function_params_uniforms(params.get_current_feedback_blend_function_info()),
            'FB_BLEND_FUNC_ARGS': GlslGenerator.generate_function_args(params.get_current_feedback_blend_function_info(), initial_comma=True),
            'FB_WARP_FRACTAL_NOISE_VARIANT': params.get_current_warp_function_info().fractal_noise_variant,
            'FB_WARP_NOISE_FUNC': params.warp_noise.noise_algorithm,
            'FB_WARP_XFORM_FUNC': params.warp_function,
            'FB_WARP_FUNC_UNIFORMS': GlslGenerator.generate_function_params_uniforms(params.get_current_warp_function_info()),
            'FB_WARP_FUNC_ARGS': GlslGenerator.generate_function_args(params.get_current_warp_function_info(), initial_comma=True),
            'COLOR_FUNC': params.color_function,
            'COLOR_FUNC_UNIFORMS': GlslGenerator.generate_function_params_uniforms(params.get_current_color_function_info()),
            'COLOR_FUNC_ARGS': GlslGenerator.generate_function_args(params.get_current_color_function_info(), initial_comma=True),
            'FB_COLOR_ADJUST_ENABLED': 'enabled' if params.enable_feedback_color_adjust else 'disabled',
        }
        self.program, _ = self.shader_cache.get_or_create_program(fragment_template_params=fragment_template_params)
        self.vao = self.shader_cache.get_or_create_vao(self.program, self.vbo, 'in_pos')

        self.program['u_time'].value = noise_time

        attributes = [
            'brightness', 
            'contrast_steepness', 
            'contrast_midpoint',
        ]

        noise_attributes = [
            'octaves',
            'gain',
            'time_scale_factor',
            'position_scale_factor',
            'rotation_angle_increment',
            'time_offset_increment',
        ]

        for attr in attributes:
            self.program[f'u_{attr}'] = getattr(params, attr)

        # Set noise attributes
        for attr in noise_attributes:
            self.program[f'u_{attr}'] = getattr(params.noise, attr)

        # Handling scale separately as it needs to be calculated based on aspect ratio
        self.program['u_scale'] = (params.noise.scale * view_scale.x, params.noise.scale * view_scale.y)

        if params.enable_feedback:
            # Set warp noise attributes
            for attr in noise_attributes:
                self.program[f'u_warp_{attr}'] = getattr(params.warp_noise, attr)

            self.program['u_warp_scale'] = (params.warp_noise.scale * view_scale.x, params.warp_noise.scale * view_scale.y)

            self.program['u_warp_time'] = warp_time  # Use the time directly from warp timer

            # Assign the function parameters to their respective shader uniforms
            self.set_function_uniforms(params.get_current_warp_function_info(), params.get_current_warp_params())
            self.set_function_uniforms(params.get_current_feedback_blend_function_info(), params.get_current_feedback_params())

            feedback_texture.use(location=0)

            if params.enable_feedback_color_adjust:
                self.program['u_feedback_hue_shift'] = params.feedback_hue_shift / 50.0
                self.program['u_feedback_saturation'] = params.feedback_saturation / 50.0

        # Assign the color function parameters to their respective shader uniforms
        self.set_function_uniforms(params.get_current_color_function_info(), params.get_current_color_params())

        
    def set_function_uniforms(self, function_info: FunctionInfo, values: List[Any]) -> None:
        """Sets shader uniforms for function parameters."""
        
        uniform_names = GlslGenerator.get_function_params_uniform_names(function_info)
        
        for uniform_name, value in zip(uniform_names, values):
            self.program[uniform_name] = value


    @property
    def current_vao(self):
        """
        Returns the current vertex array object.

        Returns:
            moderngl.VertexArray: The current VAO used in rendering.
        """
        return self.vao
