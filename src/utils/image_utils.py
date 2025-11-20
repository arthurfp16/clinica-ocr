from typing import Tuple
from PIL import Image


def load_image_rgb(path: str) -> Image.Image:
    """Carrega imagem em RGB."""
    return Image.open(path).convert("RGB")


def get_size(path: str) -> Tuple[int, int]:
    im = Image.open(path)
    return im.size
