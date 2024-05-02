from PIL import Image

def load_image_into_texture(ctx, path):
    """
    Loads an image, converts it to a texture, and builds mipmaps for it.

    Parameters:
    - ctx: ModernGL context.
    - path: Path to an image.

    Returns:
    - Texture object.
    """
    # Open the image and convert it to 'RGBA'
    img = Image.open(path).convert('RGBA')

    texture = ctx.texture(img.size, 4, img.tobytes())
    texture.build_mipmaps()

    return texture