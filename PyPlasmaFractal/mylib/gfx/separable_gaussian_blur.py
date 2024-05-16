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
        self.weights_texture = self._create_weights_texture()


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
        uniform sampler2D weightsTexture;
        uniform float maxRadius;
        uniform float offsetX;
        uniform float offsetY;
        out vec4 fragColor;
        in vec2 texCoord;

        void main() {{
            vec4 color = texture(inputTexture, texCoord);
            float brightness = dot(color.rgb, vec3(0.299, 0.587, 0.114)); // Luminance formula
            float radius = max((1.0 - brightness) * maxRadius, 0.5);  // Adding a minimum radius threshold
            int intRadius = int(radius);
            
            vec4 tmp = vec4(0.0);
            float sumWeight = 0.0;
            for (int i = -intRadius; i <= intRadius; i++) {{
                float weight = texelFetch(weightsTexture, ivec2({self.max_radius} + i, intRadius), 0).r;
                vec2 offset = vec2(float(i) * offsetX, float(i) * offsetY);
                tmp += texture(inputTexture, texCoord + offset) * weight;
                sumWeight += weight;
            }}
            fragColor = tmp / sumWeight;  // Normalize the final color to avoid any discrepancies
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


    def _create_weights_texture(self):
        
        all_weights = []
        for radius in range(self.max_radius + 1):
            weights = self._precompute_gaussian_weights(radius)
            all_weights.append(weights)
        all_weights = np.array(all_weights, dtype='f4')
        texture = self.ctx.texture((2 * self.max_radius + 1, self.max_radius + 1), 1, all_weights.tobytes(), dtype='f4')
        texture.use(location=1)  # Bind to texture unit 1
        return texture


    def _precompute_gaussian_weights(self, radius: float):
        
        if radius in self.precomputed_weights:
            return self.precomputed_weights[radius]

        if radius == 0:
            weights = np.zeros(2 * self.max_radius + 1, dtype='f4')
            weights[self.max_radius] = 1.0  # Center weight for radius 0
            self.precomputed_weights[radius] = weights
            return weights

        sigma = radius / 3.0
        size = 2 * int(radius) + 1
        weights = np.array([np.exp(-0.5 * (i / sigma)**2) / (sigma * np.sqrt(2 * np.pi)) for i in range(-int(radius), int(radius) + 1)])
        weights /= weights.sum()  # Normalize weights

        # Pad weights to the fixed size
        padded_weights = np.zeros(2 * self.max_radius + 1, dtype='f4')
        start_idx = self.max_radius - int(radius)
        end_idx = start_idx + size
        padded_weights[start_idx:end_idx] = weights

        self.precomputed_weights[radius] = padded_weights
        
        return padded_weights


    def apply_blur(self, radius: float):
        
        if radius > self.max_radius:
            raise ValueError(f"Blur radius {radius} exceeds maximum radius {self.max_radius}")
        self.shader['maxRadius'].value = radius  # Pass the user-specified radius to the shader

        directions = [(1.0 / self.texture_manager.width, 0.0),   # Horizontal offsets
                      (0.0, 1.0 / self.texture_manager.height)]  # Vertical offsets

        for offsetX, offsetY in directions:
            self.texture_manager.previous_texture.use(location=0)
            self.weights_texture.use(location=1)
            self.shader['offsetX'].value = offsetX
            self.shader['offsetY'].value = offsetY
            self.texture_manager.render_to_texture(self.vao)
            self.texture_manager.swap_textures()
