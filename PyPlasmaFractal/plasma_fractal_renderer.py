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
                      time: float, 
                      aspect_ratio: float):
        """
        Applies the rendering parameters to generate the final shader programs from templates and configures them.

        Args:
            params (PlasmaFractalParams): The parameters for the plasma fractal rendering.
            feedback_texture (moderngl.Texture): The feedback texture used for the feedback effect.
            time (float): The current time.

        Returns:
            None
        """
        #logging.debug("Updating params:" + '\n'.join(f"    {key}={value}" for key, value in vars(params).items()))

        if aspect_ratio > 1.0:
            view_scale = Vec2(aspect_ratio, 1.0)
        else:
            view_scale = Vec2(1.0, 1.0 / aspect_ratio)  
       
        noise_function_info = self.noise_function_registry.get_function_info(params.noise_algorithm)

        # Parameters that define how the fragment shader is generated from templates
        fragment_template_params = {
            'NOISE_FUNC': params.noise_algorithm,
            'NOISE_MIN': noise_function_info.min_value,
            'NOISE_MAX': noise_function_info.max_value,
            'FB_ENABLED': 'Enabled' if params.enable_feedback else 'Disabled',
            'FB_BLEND_FUNC': params.feedback_function,
            'FB_BLEND_FUNC_UNIFORMS': GlslGenerator.generate_function_params_uniforms(params.get_current_feedback_blend_function_info()),
            'FB_BLEND_FUNC_ARGS': GlslGenerator.generate_function_args(params.get_current_feedback_blend_function_info()),
            'FB_WARP_FRACTAL_NOISE_VARIANT': params.get_current_warp_function_info().fractal_noise_variant,
            'FB_WARP_NOISE_FUNC': params.warp_noise_algorithm,
            'FB_WARP_XFORM_FUNC': params.warp_function,
            'FB_WARP_FUNC_UNIFORMS': GlslGenerator.generate_function_params_uniforms(params.get_current_warp_function_info()),
            'FB_WARP_FUNC_ARGS': GlslGenerator.generate_function_args(params.get_current_warp_function_info()),
            'MAX_WARP_PARAMS': self.warp_function_registry.max_param_count(),
            'MAX_FEEDBACK_PARAMS': self.blend_function_registry.max_param_count(),
        }
        self.program, _ = self.shader_cache.get_or_create_program(fragment_template_params=fragment_template_params)
        self.vao = self.shader_cache.get_or_create_vao(self.program, self.vbo, 'in_pos')

        self.program['u_time'].value = time

        attributes = [
            'octaves', 
            'gain',
            'time_scale_factor', 
            'position_scale_factor', 
            'rotation_angle_increment', 
            'time_offset_increment', 
            'brightness', 
            'contrast_steepness', 
            'contrast_midpoint',
        ]

        feedback_attributes = [            
            'warp_speed',
            'warp_octaves',
            'warp_gain',
            'warp_time_scale_factor',
            'warp_position_scale_factor',
            'warp_rotation_angle_increment',
            'warp_time_offset_initial',
            'warp_time_offset_increment',
        ]

        for attr in attributes:
            self.program[f'u_{attr}'] = getattr(params, attr)

        # Handling scale separately as it needs to be calculated based on aspect ratio
        self.program['u_scale'] = (params.scale * view_scale.x, params.scale * view_scale.y)

        if params.enable_feedback:

            # Update feedback attributes
            for attr in feedback_attributes:
                self.program[f'u_{attr}'] = getattr(params, attr)

            self.program['u_warp_scale'] = (params.warp_scale * view_scale.x, params.warp_scale * view_scale.y)

            # Assign the function parameters to their respective shader uniforms
            self.set_function_uniforms(params.get_current_warp_function_info(), params.get_current_warp_params())
            self.set_function_uniforms(params.get_current_feedback_blend_function_info(), params.get_current_feedback_params())

            feedback_texture.use(location=0)

        
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
