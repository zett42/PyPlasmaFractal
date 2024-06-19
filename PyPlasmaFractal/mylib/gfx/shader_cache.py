import logging
from typing import *
import moderngl

from PyPlasmaFractal.mylib.config.storage import Storage
from PyPlasmaFractal.mylib.gfx.shader_template_system import ShaderTemplateResolver

class VariantShaderCache:
    """
    A caching system for managing shader programs and vertex array objects (VAOs) with different configurations. 
    The cache optimizes performance by avoiding redundant compilations of shaders and configurations of VAOs
    based on given templates and configurations.

    Attributes:
    - ctx (moderngl.Context): The ModernGL context used for shader compilation and VAO creation.
    - vertex_shader_template (str): Template for vertex shaders allowing dynamic configuration.
    - fragment_shader_template (str): Template for fragment shaders allowing dynamic configuration.
    - program_cache (dict): Cache to store compiled shader programs based on configuration hashes.
    - vao_cache (dict): Cache to store VAOs based on program and buffer identifiers.
    """    
    def __init__(self, ctx: moderngl.Context, vertex_shader_name: str, fragment_shader_name: str,
                 shader_storage: Storage[str]) -> None:
        """
        Initializes a new instance of VariantShaderCache with the given ModernGL context and shader templates.

        Parameters:
        - ctx (moderngl.Context): The ModernGL context.
        - vertex_shader_template (str): The template string for vertex shaders.
        - fragment_shader_template (str): The template string for fragment shaders.
        """
        self.ctx = ctx
        
        self.vertex_shader_name   = vertex_shader_name
        self.fragment_shader_name = fragment_shader_name
        self.shader_storage       = shader_storage

        self.program_cache = {}
        self.vao_cache = {}

    def get_or_create_program(self, 
                              vertex_template_params: Optional[Dict[str, str]] = None, 
                              fragment_template_params: Optional[Dict[str, str]] = None) -> tuple[moderngl.Program, bool]:
        """
        Retrieves or creates a shader program based on provided vertex and fragment shader configurations.
        Utilizes caching to avoid recompilation of identical shader variants.

        Returns:
        - moderngl.Program, bool: A compiled shader program ready for use in rendering operations and a bool value indicating whether 
                                  a new shader has been created.
        """
        vertex_template_params = vertex_template_params or {}
        fragment_template_params = fragment_template_params or {}
        params_key = (frozenset(vertex_template_params.items()), frozenset(fragment_template_params.items()))

        if params_key in self.program_cache:
            return self.program_cache[params_key], False

        logging.debug(f"Creating shaders for new variant with template params hash: {hash(params_key)}")

        is_debug = logging.getLogger().isEnabledFor(logging.DEBUG)

        template_resolver = ShaderTemplateResolver(self.shader_storage, extra_debug_info=is_debug)
        vertex_shader_source = template_resolver.resolve(self.vertex_shader_name, vertex_template_params)
        fragment_shader_source = template_resolver.resolve(self.fragment_shader_name, fragment_template_params)

        program = self.ctx.program(vertex_shader=vertex_shader_source, fragment_shader=fragment_shader_source)
        self.program_cache[params_key] = program
        
        return program, True

    def get_or_create_vao(self, program: moderngl.Program, vbo: moderngl.Buffer, *attribute_names: str) -> moderngl.VertexArray:
        """
        Retrieves or creates a Vertex Array Object (VAO) based on the given shader program and vertex buffer object (VBO),
        with attribute names specified as variable arguments. This method optimizes rendering by caching and reusing VAOs,
        reducing the overhead of repeatedly setting up VAOs for identical shader and VBO combinations.

        Parameters:
        - program (ModernGL.Program): The shader program to be used with the VAO.
        - vbo (ModernGL.Buffer): The vertex buffer object containing the vertex data.
        - *attribute_names (varargs of str): Names of the shader attributes to be linked to the vertex buffer data.

        Returns:
        - vao (ModernGL.VertexArray): A configured VAO ready for rendering operations.
        
        Usage Example:
        - get_or_create_vao(program, vbo, 'in_pos', 'in_tex')
        """
        vao_key = (program.glo, vbo.glo) + attribute_names

        if vao_key in self.vao_cache:
            return self.vao_cache[vao_key]

        logging.debug(f"Creating new VAO for the given shader #{program.glo} and VBO #{vbo.glo}")

        vao = self.ctx.simple_vertex_array(program, vbo, *attribute_names)
        self.vao_cache[vao_key] = vao

        return vao
