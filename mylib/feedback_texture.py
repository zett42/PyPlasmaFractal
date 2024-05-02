import moderngl

class FeedbackTextureManager:
    """
    Class to handle a feedback effect using two textures and framebuffers.
    """
    def __init__(self, ctx, width=800, height=600, 
                 dtype='f1', 
                 repeat_x=False, repeat_y=False, 
                 filter_x: int = moderngl.NEAREST, filter_y: int = moderngl.NEAREST):
        """
        Initializes two textures and framebuffers for the feedback effect.
        
        Parameters:
        - ctx: The ModernGL context to use.
        - width: The width of the texture.
        - height: The height of the texture.
        """
        self.ctx = ctx
        self.width = width
        self.height = height
        
        # Create two textures and framebuffers for feedback loop
        self.textures = [ctx.texture((width, height), components=4, dtype=dtype) for _ in range(2)]
        self.framebuffers = [ctx.framebuffer(color_attachments=[tex]) for tex in self.textures]
        
        for texture in self.textures:
            texture.repeat_x = repeat_x
            texture.repeat_y = repeat_y
            texture.filter = (filter_x, filter_y)
        
        # Index to keep track of which texture/FBO is currently used for rendering
        self.current_render_index = 0


    def render_to_texture(self, vao):
        """
        Renders to the current destination texture using the other texture as a source.
        
        Parameters:
        - vao: The vertex array object to render.
        """
        # Bind the framebuffer for rendering
        self.framebuffers[self.current_render_index].use()
        self.ctx.clear(0.0, 0.0, 0.0, 1.0)  # Clear with black color

        # Render the object
        vao.render(moderngl.TRIANGLES)  
        
        # Swap index for next render call
        self.current_render_index = 1 - self.current_render_index
        
        # Revert to default framebuffer
        self.ctx.screen.use()


    @property
    def current_texture(self):
        """
        Returns the texture currently used as the destination for rendering.
        """
        return self.textures[self.current_render_index]


    @property
    def previous_texture(self):
        """
        Returns the texture that was last used as the destination and is now used as the source.
        """
        return self.textures[1 - self.current_render_index]