import logging
from typing import Tuple
import moderngl

class FeedbackTextureManager:
    """
    Class to handle a feedback effect using two textures and framebuffers.
    """
    def __init__(self, 
                 ctx: moderngl.Context, 
                 width: int = 800, height: int = 600, 
                 dtype: str = 'f4', 
                 repeat_x: bool = False, repeat_y: bool = False, 
                 filter_x: int = moderngl.NEAREST, filter_y: int = moderngl.NEAREST) -> None:
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


    @property
    def aspect_ratio(self) -> float:
        """
        Returns the aspect ratio of the texture.
        """
        return self.width / self.height


    def render_to_texture(self, vao: moderngl.VertexArray) -> None:
        """
        Renders to the current destination texture using the other texture as a source.
        
        Parameters:
        - vao: The vertex array object to render.
        """
        # Bind the framebuffer for rendering
        # Using the 'with' statement avoids manual restoration of the previous framebuffer
        with self.ctx.scope(self.framebuffers[self.current_render_index]):

            self.ctx.clear(0.0, 0.0, 0.0, 1.0)  # Clear with black color

            # Render the object
            vao.render(moderngl.TRIANGLES)
        
        # Swap index for next render call
        self.current_render_index = 1 - self.current_render_index


    def resize(self, new_width: int, new_height: int) -> None:
        """
        Resizes the textures and framebuffers used in the feedback loop.
        """
        if new_width <= 0 or new_height <= 0:
            return

        # Temporarily store texture properties
        repeat_x = self.textures[0].repeat_x
        repeat_y = self.textures[0].repeat_y
        filter = self.textures[0].filter
        dtype = self.textures[0].dtype

        # Release existing textures and framebuffers
        for fbo in self.framebuffers:
            fbo.release()
        for tex in self.textures:
            tex.release()

        # Clear lists to avoid accidental use of released resources
        self.textures = []
        self.framebuffers = []

        # Update the internal dimensions
        self.width = new_width
        self.height = new_height

        # Attempt to re-create the textures and framebuffers with the new dimensions
        self.textures = [self.ctx.texture((self.width, self.height), components=4, dtype=dtype) for _ in range(2)]
        self.framebuffers = [self.ctx.framebuffer(color_attachments=[tex]) for tex in self.textures]

        # Reapply the stored texture settings
        for texture in self.textures:
            texture.repeat_x = repeat_x
            texture.repeat_y = repeat_y
            texture.filter = filter

        # Clear each new texture to ensure it starts from a clean state
        self.clear()


    def clear(self, color: Tuple[float, float, float, float] = (0.0, 0.0, 0.0, 1.0)) -> None:
        """
        Clears all textures with the given color.
        """
        for fbo in self.framebuffers:
            with self.ctx.scope(fbo):
                self.ctx.clear(*color)
                

    @property
    def current_texture(self) -> moderngl.Texture:
        """
        Returns the texture currently used as the destination for rendering.
        """
        return self.textures[self.current_render_index]


    @property
    def previous_texture(self) -> moderngl.Texture:
        """
        Returns the texture that was last used as the destination and is now used as the source.
        """
        return self.textures[1 - self.current_render_index]