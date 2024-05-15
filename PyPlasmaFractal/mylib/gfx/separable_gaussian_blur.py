import moderngl
import numpy as np
from PyPlasmaFractal.mylib.gfx.texture_render_manager import PingpongTextureRenderManager

class SeparableGaussianBlur:
    
    def __init__(self, ctx: moderngl.Context, texture_manager: PingpongTextureRenderManager, max_radius=16):
        
        self.ctx = ctx
        self.texture_manager = texture_manager
        self.max_radius = max_radius
        self.shader = self._create_shader()
        self.vbo = self._create_fullscreen_quad()
        self.vao = ctx.simple_vertex_array(self.shader, self.vbo, 'in_vert', 'in_tex')
        self.precomputed_weights = {}


    def _create_shader(self):
        
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
        
        fragment_shader_src = f"""
        #version 330
        uniform sampler2D inputTexture;
        uniform float radius;
        uniform float offsetX;
        uniform float offsetY;
        uniform float weights[{2 * self.max_radius + 1}];  // Fixed size array based on max_radius
        out vec4 fragColor;
        in vec2 texCoord;

        void main() {{
            vec4 tmp = vec4(0.0);
            for (int i = -int(radius); i <= int(radius); i++) {{
                float weight = weights[{self.max_radius} + i];
                vec2 offset = vec2(float(i) * offsetX, float(i) * offsetY);
                tmp += texture(inputTexture, texCoord + offset) * weight;
            }}
            fragColor = tmp;
        }}
        """
        return self.ctx.program(vertex_shader=vertex_shader_src, fragment_shader=fragment_shader_src)


    def _create_fullscreen_quad(self):
        
        vertices = np.array([
            -1.0, -1.0, 0.0, 1.0,
             1.0, -1.0, 1.0, 1.0,
            -1.0,  1.0, 0.0, 0.0,
             1.0, -1.0, 1.0, 1.0,
             1.0,  1.0, 1.0, 0.0,
            -1.0,  1.0, 0.0, 0.0
        ], dtype='f4')
        
        return self.ctx.buffer(vertices.tobytes())
    
    
    def _precompute_gaussian_weights(self, radius):
        
        if radius in self.precomputed_weights:
            return self.precomputed_weights[radius]

        sigma = radius / 3.0
        size = 2 * int(radius) + 1
        weights = np.array([np.exp(-0.5 * (i / sigma)**2) / (sigma * np.sqrt(2 * np.pi)) for i in range(size)])
        weights /= weights.sum()  # Normalize weights

        # Pad weights to the fixed size
        padded_weights = np.zeros(2 * self.max_radius + 1, dtype='f4')
        start_idx = self.max_radius - int(radius)
        end_idx = start_idx + size
        padded_weights[start_idx:end_idx] = weights

        self.precomputed_weights[radius] = padded_weights
        
        return padded_weights
    
    
    def apply_blur(self, blur_radius: float):
        
        if blur_radius > self.max_radius:
            raise ValueError(f"Blur radius {blur_radius} exceeds maximum radius {self.max_radius}")

        weights = self._precompute_gaussian_weights(blur_radius)
        self.shader['radius'].value = blur_radius
        self.shader['weights'].write(weights.astype('f4').tobytes())

        directions = [(1.0 / self.texture_manager.width, 0.0),   # Horizontal offsets
                      (0.0, 1.0 / self.texture_manager.height)]  # Vertical offsets

        for offsetX, offsetY in directions:
            self.texture_manager.previous_texture.use(location=0)
            self.shader['offsetX'].value = offsetX
            self.shader['offsetY'].value = offsetY
            self.texture_manager.render_to_texture(self.vao)
            self.texture_manager.swap_textures()
