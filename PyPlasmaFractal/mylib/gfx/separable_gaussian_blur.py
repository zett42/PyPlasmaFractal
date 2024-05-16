import moderngl
import numpy as np
from PyPlasmaFractal.mylib.gfx.texture_render_manager import PingpongTextureRenderManager

class SeparableGaussianBlur:
    """
    A class for performing separable Gaussian blur on textures using ModernGL.

    Attributes:
        ctx (moderngl.Context): The ModernGL context.
        texture_manager (PingpongTextureRenderManager): The texture manager for pingpong rendering.
        max_radius (int): The maximum blur radius.
    """
    
    def __init__(self, ctx: moderngl.Context, texture_manager: PingpongTextureRenderManager, max_radius: int = 16) -> None:
        """
        Initializes a SeparableGaussianBlur object.

        Args:
            ctx (moderngl.Context): The ModernGL context.
            texture_manager (PingpongTextureRenderManager): The texture manager for pingpong rendering.
            max_radius (int, optional): The maximum blur radius. Defaults to 16.
        """
        self.ctx = ctx
        self.texture_manager = texture_manager
        self.max_radius = max_radius
        
        self.shader = self._create_shader()
        self.vbo = self._create_fullscreen_quad()
        self.vao = ctx.simple_vertex_array(self.shader, self.vbo, 'in_vert', 'in_tex')
        
        self.precomputed_weights = {}
        self.weights_texture = self._create_weights_texture()


    def _create_shader(self) -> moderngl.Program:
        """
        Creates and returns a shader program for performing separable Gaussian blur.

        Returns:
            Program: The shader program object.

        Raises:
            None.
        """
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
        uniform float radiusPower;
        uniform vec2 offset;
        out vec4 fragColor;
        in vec2 texCoord;

        void main() {{
            // Fetch the initial color and calculate its brightness
            vec4 color = texture(inputTexture, texCoord);
            float brightness = dot(color.rgb, vec3(0.299, 0.587, 0.114)); // Luminance formula

            // Calculate the blur radius based on brightness and apply radius power
            brightness = pow(1.0 - brightness, radiusPower);
            float radius = max(brightness * maxRadius, 0.5);  // Minimum radius of 0.5 to avoid overly small blur
            int intRadius = int(radius);

            // Initialize accumulation variables
            vec4 tmp = vec4(0.0);
            float sumWeight = 0.0;

            // Accumulate weighted color samples
            for (int i = -intRadius; i <= intRadius; i++) {{
                float weight = texelFetch(weightsTexture, ivec2({self.max_radius} + i, intRadius), 0).r;
                vec2 offsetCoord = vec2(float(i)) * offset;
                vec2 clampedCoord = clamp(texCoord + offsetCoord, vec2(0.0), vec2(1.0));
                tmp += texture(inputTexture, clampedCoord) * weight;
                sumWeight += weight;
            }}

            // Normalize the final color to avoid any discrepancies
            fragColor = tmp / sumWeight;
        }}
        """

        return self.ctx.program(vertex_shader=vertex_shader_src, fragment_shader=fragment_shader_src)


    def _create_fullscreen_quad(self) -> moderngl.Buffer:
        """
        Creates a fullscreen quad for rendering.

        Returns:
            A buffer object containing the vertices of the fullscreen quad.
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


    def _create_weights_texture(self) -> moderngl.Texture:
        """
        Create a texture containing precomputed Gaussian weights for different radii.

        Returns:
            texture (Texture): The created texture containing the precomputed weights.
        """
        all_weights = []
        for radius in range(self.max_radius + 1):
            weights = self._precompute_gaussian_weights(radius)
            all_weights.append(weights)
            
        all_weights = np.array(all_weights, dtype='f4')
        
        texture = self.ctx.texture((2 * self.max_radius + 1, self.max_radius + 1), 1, all_weights.tobytes(), dtype='f4')
        
        # Set NEAREST filter for more exact texture lookups
        texture.filter = (moderngl.NEAREST, moderngl.NEAREST)
               
        return texture


    def _precompute_gaussian_weights(self, radius: float) -> np.ndarray:
        """
        Precomputes and returns the Gaussian weights for the given radius.

        Args:
            radius (float): The radius of the Gaussian blur.

        Returns:
            numpy.ndarray: The precomputed Gaussian weights.

        """
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


    def apply_blur(self, radius: float, radius_power=1.0) -> None:
        """
        Applies a separable Gaussian blur to the texture.

        Args:
            radius (float): The radius of the blur. Must be less than or equal to `max_radius`.
            radius_power (float, optional): The non-linearity factor of the blur. Defaults to 1.0.

        Raises:
            ValueError: If the specified `radius` exceeds the maximum radius.

        Returns:
            None
        """
        if radius > self.max_radius:
            raise ValueError(f"Blur radius {radius} exceeds maximum radius {self.max_radius}")
        
        # Set the shader uniforms that are constant for the entire blur operation
        self.shader['maxRadius'].value = radius
        self.shader['radiusPower'].value = radius_power

        # Bind the weights texture to the shader
        self.weights_texture.use(location=1)

        directions = [(1.0 / self.texture_manager.width, 0.0),   # Horizontal offsets
                      (0.0, 1.0 / self.texture_manager.height)]  # Vertical offsets

        # Apply the blur in both directions
        for current_direction in directions:
            
            # Bind the source texture to the shader
            self.texture_manager.previous_texture.use(location=0)
            
            # Set the shader uniforms for the current direction
            self.shader['offset'].value = current_direction
            
            # Render to the texture and swap the textures to apply the blur in both directions
            self.texture_manager.render_to_texture(self.vao)
            self.texture_manager.swap_textures()
