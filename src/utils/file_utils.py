import os
from typing import List

IMG_EXTS = {".png", ".jpg", ".jpeg", ".bmp", ".webp", ".tif", ".tiff"}


def is_image(path: str) -> bool:
    return os.path.splitext(path.lower())[1] in IMG_EXTS


def list_images(dir_path: str) -> List[str]:
    if not os.path.isdir(dir_path):
        return []
    files = [
        f for f in os.listdir(dir_path)
        if os.path.isfile(os.path.join(dir_path, f)) and is_image(f)
    ]
    files.sort()
    return files


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)
