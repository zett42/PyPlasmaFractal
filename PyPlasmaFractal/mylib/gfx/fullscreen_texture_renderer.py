import moderngl
import numpy as np

class FullscreenTextureRenderer:
    """
    A class for rendering fullscreen textures using ModernGL.
    """

    def __init__(self, ctx: moderngl.Context) -> None:
        """
        Initializes the texture renderer with a ModernGL context.
        
        Parameters:
        - ctx: Existing ModernGL context.
        """
        self.ctx = ctx
        self.vbo = self.create_fullscreen_quad()
        self.program = self.create_shader_program()
        self.vao = ctx.simple_vertex_array(self.program, self.vbo, 'in_vert', 'in_tex')


    def create_fullscreen_quad(self) -> moderngl.Buffer:
        """
        Creates a VBO for a fullscreen quad with texture coordinates, covering the viewport.
        
        Returns:
        - Vertex buffer object for a fullscreen quad.
        """
        vertices = np.array([
            -1.0, -1.0, 0.0, 1.0,
             1.0, -1.0, 1.0, 1.0,
            -1.0,  1.0, 0.0, 0.0,
             1.0, -1.0, 1.0, 1.0,
             1.0,  1.0, 1.0, 0.0,
            -1.0,  1.0, 0.0, 0.0
        ], dtype='f4')
        
        return self.ctx.buffer(vertices.tobytes())


    def create_shader_program(self) -> moderngl.Program:
        """
        Creates a shader program for rendering textures.
        
        Returns:
        - Compiled shader program.
        """
        vertex_shader_code = '''
        #version 330
        in vec2 in_vert;
        in vec2 in_tex;
        out vec2 v_tex;
        void main() {
            gl_Position = vec4(in_vert, 0.0, 1.0);
            v_tex = in_tex;
        }
        '''
        fragment_shader_code = '''
        #version 330
        uniform sampler2D texture0;
        in vec2 v_tex;
        out vec4 f_color;
        void main() {
            f_color = texture(texture0, v_tex);
        }
        '''
        return self.ctx.program(vertex_shader=vertex_shader_code, fragment_shader=fragment_shader_code)


    def render(self, texture: moderngl.Texture, destination: moderngl.Framebuffer) -> None:
        """
        Renders the texture to the screen using the prepared VBO and shader program.
        
        Parameters:
        - texture: The texture to render.
        - destination: The framebuffer to render to.
        """
        with self.ctx.scope(destination):         # Use the destination framebuffer

            self.ctx.clear(0.0, 0.0, 0.0)

            texture.use(location=0)               # Assign texture to texture unit 0
            self.program['texture0'].value = 0    # Using texture unit 0 in shader

            self.vao.render(moderngl.TRIANGLES)   # Draw using the shaders associated with the VAO
