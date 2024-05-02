import moderngl

# Define a class to manage rendering to a texture
class RenderToTexture:
    """
    Class to handle rendering into a texture using a Framebuffer Object (FBO).
    """
    def __init__(self, ctx, width=800, height=600):
        """
        Initializes the FBO and texture for rendering.
        
        Parameters:
        - ctx: The ModernGL context to use.
        - width: The width of the texture.
        - height: The height of the texture.
        """
        self.ctx = ctx
        self.width = width
        self.height = height
        
        # Create a texture to render into
        self.texture = ctx.texture((width, height), 4)
        self.texture.repeat_x = False
        self.texture.repeat_y = False
        self.texture.filter = (moderngl.NEAREST, moderngl.NEAREST)
        
        # Create a framebuffer and attach the texture
        self.fbo = ctx.framebuffer(color_attachments=[self.texture])

    def render_to_texture(self, vao):
        """
        Renders to the texture attached to this FBO.
        
        Parameters:
        - vao: The vertex array object to render.
        """
        # Bind the framebuffer
        self.fbo.use()
        self.ctx.clear(0.0, 0.0, 0.0, 1.0)  # Clear with a black color
        vao.render(moderngl.TRIANGLES)  # Render the object
        
        # Unbind the framebuffer, reverting to default framebuffer
        self.ctx.screen.use()

    def get_texture(self):
        """
        Returns the texture that has the rendered content.
        
        Returns:
        - The texture object.
        """
        return self.texture
