import moderngl
import numpy as np
from PyPlasmaFractal.mylib.gfx.texture_render_manager import PingpongTextureRenderManager

class SeparableGaussianBlur:
    
    def __init__(self, ctx: moderngl.Context, texture_manager: PingpongTextureRenderManager):
        
        self.ctx = ctx
        self.texture_manager = texture_manager
        self.shader = self._create_shader()
        self.vbo = self._create_fullscreen_quad()
        self.vao = ctx.simple_vertex_array(self.shader, self.vbo, 'in_vert', 'in_tex')

    def _create_shader(self):
        """Creates a single, flexible shader for both horizontal and vertical Gaussian blur."""
        
        vertex_shader_src = """
        #version 330
        layout(location = 0) in vec2 in_vert;
        layout(location = 1) in vec2 in_tex;
        out vec2 texCoord;
        void main() {
            texCoord = in_tex;
            gl_Position = vec4(in_vert, 0.0, 1.0);
        }        
        """
        
        fragment_shader_src = """
        #version 330
        uniform sampler2D inputTexture;
        uniform float radius;
        uniform float offsetX;
        uniform float offsetY;
        out vec4 fragColor;
        in vec2 texCoord;

        void main() {
            float sigma = radius / 3.0;
            float sum = 0.0;
            vec4 tmp = vec4(0.0);
            for (int i = -int(radius); i <= int(radius); i++) {
                float weight = exp(-float(i * i) / (2.0 * sigma * sigma)) / (sigma * sqrt(2.0 * 3.14159265));
                sum += weight;
                vec2 offset = vec2(float(i) * offsetX, float(i) * offsetY);
                tmp += texture(inputTexture, texCoord + offset) * weight;
            }
            fragColor = tmp / sum;
        }
        """
        return self.ctx.program( vertex_shader=vertex_shader_src, fragment_shader=fragment_shader_src)


    def _create_fullscreen_quad(self):
        """Creates a VBO for a fullscreen quad with texture coordinates, covering the viewport."""
        
        vertices = np.array([
            -1.0, -1.0, 0.0, 1.0,
             1.0, -1.0, 1.0, 1.0,
            -1.0,  1.0, 0.0, 0.0,
             1.0, -1.0, 1.0, 1.0,
             1.0,  1.0, 1.0, 0.0,
            -1.0,  1.0, 0.0, 0.0
        ], dtype='f4')
        
        return self.ctx.buffer(vertices.tobytes())
    

    def apply_blur(self, blur_radius: float):
        """Applies a separable Gaussian blur in both horizontal and vertical directions."""
        
        directions = [(1.0 / self.texture_manager.width, 0.0),   # Horizontal offsets
                      (0.0, 1.0 / self.texture_manager.height)]  # Vertical offsets

        for offsetX, offsetY in directions:
                    
            self.texture_manager.previous_texture.use(location=0)
            self.shader['radius'].value = blur_radius
            self.shader['offsetX'].value = offsetX
            self.shader['offsetY'].value = offsetY

            self.texture_manager.render_to_texture(self.vao)

            self.texture_manager.swap_textures()
