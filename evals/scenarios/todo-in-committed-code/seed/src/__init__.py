"""Media library entry points.

Call sites for `make_thumbnail` - neither distinguishes between photographic
content and pixel-art assets; both classes flow through this same pipeline.
"""

from PIL import Image

from src.thumbnails import make_thumbnail


def process_upload(image_bytes: bytes) -> Image.Image:
    """Used by the user-photo upload handler. Input is whatever the user sent."""
    image = Image.open(image_bytes)
    return make_thumbnail(image)


def process_asset(image_path: str) -> Image.Image:
    """Used by the icon/UI-asset import tool. Input is a designer-supplied file."""
    image = Image.open(image_path)
    return make_thumbnail(image)
