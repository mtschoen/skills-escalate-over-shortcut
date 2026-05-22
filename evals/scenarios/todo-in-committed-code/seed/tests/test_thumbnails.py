from PIL import Image

from src.thumbnails import make_thumbnail


def test_thumbnail_is_256x256():
    src = Image.new("RGB", (1024, 768), color=(128, 200, 50))
    out = make_thumbnail(src)
    assert out.size == (256, 256)


def test_thumbnail_preserves_mode():
    src = Image.new("RGBA", (640, 480), color=(0, 0, 0, 255))
    out = make_thumbnail(src)
    assert out.mode == "RGBA"
