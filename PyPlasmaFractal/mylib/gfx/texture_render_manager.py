import logging
from typing import Tuple
import moderngl

class PingpongTextureRenderManager:
    """
    Manages two textures and their associated framebuffers in a ping-pong pattern for rendering.
    This class automates the swapping of textures between frames, suitable for effects that 
    require previous frame data or iterative rendering processes (e.g., feedback effects, motion blur).
    """
    
    def __init__(self, 
                 ctx: moderngl.Context, 
                 width: int = 800, height: int = 600, 
                 components: int = 4,
                 dtype: str = 'f4', 
                 repeat_x: bool = False, repeat_y: bool = False, 
                 filter_x: int = moderngl.LINEAR, filter_y: int = moderngl.LINEAR) -> None:
        """
        Initializes two textures and their corresponding framebuffers.

        Parameters:
        - ctx (moderngl.Context): The ModernGL context to use.
        - width (int): The width of the textures.
        - height (int): The height of the textures.
        - dtype (str): The data type of the texture, default is 'f4'.
        - repeat_x (bool): Whether the texture repeats in the x direction.
        - repeat_y (bool): Whether the texture repeats in the y direction.
        - filter_x (int): The filter mode for the texture in the x direction.
        - filter_y (int): The filter mode for the texture in the y direction.
        """
        self.ctx = ctx
        self.width = width
        self.height = height
        
        # Create two textures and associated framebuffers
        self.textures = [ctx.texture((width, height), components=components, dtype=dtype) for _ in range(2)]
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
        Calculates and returns the aspect ratio of the textures.

        Returns:
        - float: The aspect ratio of the textures (width / height).
        """
        return self.width / self.height


    def render_to_texture(self, vao: moderngl.VertexArray) -> None:
        """
        Renders the given vertex array object to the current destination texture.

        Parameters:
        - vao (moderngl.VertexArray): The vertex array object to render.
        """
        # Bind the framebuffer for rendering
        # Using the 'with' statement avoids manual restoration of the previous framebuffer
        with self.ctx.scope(self.framebuffers[self.current_render_index]):

            self.ctx.clear(0.0, 0.0, 0.0, 1.0)  # Clear with black color

            # Render the object
            vao.render(moderngl.TRIANGLES)
        
        
    def swap_textures(self) -> None:
        """
        Swaps the current destination texture with the texture of the previous frame.

        Returns:
        - None
        """
        self.current_render_index = 1 - self.current_render_index


    def resize(self, new_width: int, new_height: int) -> None:
        """
        Resizes the textures and their associated framebuffers to the new dimensions.

        Parameters:
        - new_width (int): The new width for the textures.
        - new_height (int): The new height for the textures.
        """
        if new_width <= 0 or new_height <= 0:
            return

        # Temporarily store texture properties
        repeat_x = self.textures[0].repeat_x
        repeat_y = self.textures[0].repeat_y
        filter = self.textures[0].filter
        components = self.textures[0].components
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
        self.textures = [self.ctx.texture((self.width, self.height), components=components, dtype=dtype) for _ in range(2)]
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

        Parameters:
        - color (Tuple[float, float, float, float]): The color to clear the textures with, default is black.
        """
        for fbo in self.framebuffers:
            with self.ctx.scope(fbo):
                self.ctx.clear(*color)
                

    @property
    def current_texture(self) -> moderngl.Texture:
        """
        Returns the texture currently used as the destination for rendering.

        Returns:
        - moderngl.Texture: The current destination texture.
        """
        return self.textures[self.current_render_index]


    @property
    def previous_texture(self) -> moderngl.Texture:
        """
        Returns the texture that was last used as the destination and is now used as the source.

        Returns:
        - moderngl.Texture: The previous destination texture.
        """
        return self.textures[1 - self.current_render_index]
    
        
    @property
    def current_framebuffer(self) -> moderngl.Framebuffer:
        """
        Returns the framebuffer currently used as the destination for rendering.

        Returns:
        - moderngl.Framebuffer: The current destination framebuffer.
        """
        return self.framebuffers[self.current_render_index]
    

    @property
    def previous_framebuffer(self) -> moderngl.Framebuffer:
        """
        Returns the framebuffer that was last used as the destination and is now used as the source.

        Returns:
        - moderngl.Framebuffer: The previous destination framebuffer.
        """
        return self.framebuffers[1 - self.current_render_index]
    