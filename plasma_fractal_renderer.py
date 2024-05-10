import logging
from typing import *
import os
import moderngl
import numpy as np
from collections import namedtuple

from mylib.named_tuples import Vec2
from mylib.resources import resource_path
from mylib.shader_cache import VariantShaderCache
from mylib.shader_template_system import make_dict_source_resolver
from mylib.files_to_dict import read_directory_files_to_dict
from plasma_fractal_params import PlasmaFractalParams, WarpFunctionRegistry


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


    def update_params(self, params: PlasmaFractalParams, feedback_texture: moderngl.Texture, time: float, aspect_ratio: float):
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

        # Parameters that define how the fragment shader is generated from templates
        fragment_template_params = {
            'NOISE_FUNC': params.noise_algorithm.name,
            'FB_ENABLED': 'Enabled' if params.enable_feedback else 'Disabled',
            'FB_BLEND_MODE': params.feedback_blend_mode.name,
            'FB_WARP_FRACTAL_NOISE_VARIANT': params.get_current_warp_function_info().fractal_noise_variant.name,
            'FB_WARP_NOISE_FUNC': params.warpNoiseAlgorithm.name,
            'FB_WARP_XFORM_FUNC': params.warpFunction,
            'MAX_WARP_PARAMS': WarpFunctionRegistry.get_max_warp_params(),
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
            'feedback_decay',
            'feedback_param1',
            'feedback_param2',
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

            self._set_warp_params_uniform(params, self.program)

            feedback_texture.use(location=0)


    def _set_warp_params_uniform(self, params: PlasmaFractalParams, program):
        """
        Prepare and update the shader's warp parameters based on the current warp function.

        Args:
            params (PlasmaFractalParams): The object containing warp function and parameters.
            program (ShaderProgram): The shader program object which will use the parameters.

        """

        # Populate the array with current warp parameters and ensure the shader receives a fixed size array by filling unused params with zero.
        max_warp_params = WarpFunctionRegistry.get_max_warp_params()
        current_warp_params = params.get_current_warp_params()
        warpParams_np = np.zeros(max_warp_params, dtype='float32')
        warpParams_np[:len(current_warp_params)] = current_warp_params

        # Write the array to the shader's uniform buffer
        program['u_warpParams'].write(warpParams_np.tobytes())


    @property
    def current_vao(self):
        """
        Returns the current vertex array object.

        Returns:
            moderngl.VertexArray: The current VAO used in rendering.
        """
        return self.vao