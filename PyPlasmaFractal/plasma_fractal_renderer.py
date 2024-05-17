import logging
from typing import *
import os
import moderngl
import numpy as np
from collections import namedtuple

from PyPlasmaFractal.mylib.config.function_registry import FunctionRegistry
from PyPlasmaFractal.mylib.named_tuples import Vec2
from PyPlasmaFractal.plasma_fractal_resources import resource_path
from PyPlasmaFractal.mylib.gfx.shader_cache import VariantShaderCache
from PyPlasmaFractal.mylib.gfx.shader_template_system import make_dict_source_resolver
from PyPlasmaFractal.mylib.config.files_to_dict import read_directory_files_to_dict
from PyPlasmaFractal.plasma_fractal_types import ShaderFunctionType
from .plasma_fractal_params import PlasmaFractalParams


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
    def __init__(self, ctx):
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
        shader_dict = read_directory_files_to_dict(shader_base_directory, recursive=True)

        # Create a source resolver using the loaded dictionary
        shader_source_resolver = make_dict_source_resolver(shader_dict)

        # Provide the shader sources to the cache.
        self.shader_cache = VariantShaderCache(ctx, '_vertex_shader.glsl', '_fragment_shader.glsl', shader_source_resolver)


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
                      shader_function_registries: Dict[ShaderFunctionType, FunctionRegistry], 
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

        blend_function_registry = shader_function_registries[ShaderFunctionType.BLEND]
        warp_function_registry  = shader_function_registries[ShaderFunctionType.WARP]

        # Parameters that define how the fragment shader is generated from templates
        fragment_template_params = {
            'NOISE_FUNC': params.noise_algorithm,
            'FB_ENABLED': 'Enabled' if params.enable_feedback else 'Disabled',
            'FB_BLEND_FUNC': params.feedback_function,
            'FB_WARP_FRACTAL_NOISE_VARIANT': params.get_current_warp_function_info().fractal_noise_variant,
            'FB_WARP_NOISE_FUNC': params.warpNoiseAlgorithm,
            'FB_WARP_XFORM_FUNC': params.warpFunction,
            'MAX_WARP_PARAMS': warp_function_registry.max_param_count(),
            'MAX_FEEDBACK_PARAMS': blend_function_registry.max_param_count(),
        }
        self.program, _ = self.shader_cache.get_or_create_program(fragment_template_params=fragment_template_params)
        self.vao = self.shader_cache.get_or_create_vao(self.program, self.vbo, 'in_pos')

        self.program['u_time'].value = time

        # List of PlasmaFractalParams attributes that map directly to shader uniform variables
        
        attributes = [
            'octaves', 
            'gain',
            'timeScaleFactor', 
            'positionScaleFactor', 
            'rotationAngleIncrement', 
            'timeOffsetIncrement', 
            'brightness', 
            'contrastSteepness', 
            'contrastMidpoint',
        ]

        feedback_attributes = [            
            'warpSpeed',
            'warpOctaves',
            'warpGain',
            'warpTimeScaleFactor',
            'warpPositionScaleFactor',
            'warpRotationAngleIncrement',
            'warpTimeOffsetInitial',
            'warpTimeOffsetIncrement',
        ]

        for attr in attributes:
            self.program[f'u_{attr}'] = getattr(params, attr)

        # Handling scale separately as it needs to be calculated based on aspect ratio
        self.program['u_scale'] = (params.scale * view_scale.x, params.scale * view_scale.y)

        if params.enable_feedback:

            # Update feedback attributes
            for attr in feedback_attributes:
                self.program[f'u_{attr}'] = getattr(params, attr)

            self.program['u_warpScale'] = (params.warpScale * view_scale.x, params.warpScale * view_scale.y)

            # Assign the parameters to their respective shader uniforms
            self.set_params_uniform(params.get_current_warp_params(), 'u_warpParams', warp_function_registry.max_param_count())
            self.set_params_uniform(params.get_current_feedback_params(), 'u_feedbackParams', blend_function_registry.max_param_count())

            feedback_texture.use(location=0)
        
    
    def set_params_uniform(self, current_params: List[float], uniform_name: str, max_params_count: int):
        """
        General function to prepare and update shader function arguments for user-selectable shader functions.

        Args:
            current_params (list): List of current parameter values.
            uniform_name (str): The name of the uniform variable in the shader.
            max_params_count (int): The maximum number of parameters expected by the shader.
            program (ShaderProgram): The shader program object which will use the parameters.

        """
        # Populate the array with current parameters and ensure the shader receives a fixed size array by filling unused params with zero.
        params_np = np.zeros(max_params_count, dtype='float32')
        params_np[:len(current_params)] = current_params

        # Write the array to the shader's uniform buffer
        self.program[uniform_name].write(params_np.tobytes())        


    @property
    def current_vao(self):
        """
        Returns the current vertex array object.

        Returns:
            moderngl.VertexArray: The current VAO used in rendering.
        """
        return self.vao
