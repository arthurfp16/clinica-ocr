import os
import argparse
from typing import List
from PIL import Image

IMG_EXTS = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff", ".webp"}


def is_image(path: str) -> bool:
    return os.path.splitext(path.lower())[1] in IMG_EXTS


def scan_images(root_dir: str) -> List[str]:
    files = []
    for r, _, fns in os.walk(root_dir):
        for f in fns:
            p = os.path.join(r, f)
            if is_image(p):
                files.append(p)
    files.sort()
    return files


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def slice_image(path: str, out_dir: str, chunk_height: int, min_height: int) -> int:
    base = os.path.splitext(os.path.basename(path))[0]
    im = Image.open(path).convert("RGB")
    w, h = im.size
    count = 0
    y = 0
    while y < h:
        y2 = min(y + chunk_height, h)
        if y2 - y < min_height:
            break
        crop = im.crop((0, y, w, y2))
        out_name = f"{base}_chunk_{count:04d}.png"
        out_path = os.path.join(out_dir, out_name)
        crop.save(out_path, format="PNG")
        count += 1
        y += chunk_height
    return count


def main():
    parser = argparse.ArgumentParser(description="Corta páginas em faixas horizontais fixas.")
    parser.add_argument("--input", default="data/raw", help="Pasta com páginas brutas (scans).")
    parser.add_argument("--output", default="data/pending/img", help="Pasta de saída para as faixas.")
    parser.add_argument("--chunk-height", type=int, default=50, help="Altura de cada faixa em pixels.")
    parser.add_argument("--min-height", type=int, default=20, help="Altura mínima para guardar a faixa.")
    parser.add_argument("--overwrite", action="store_true", help="Limpa a pasta de saída antes de criar.")
    args = parser.parse_args()

    in_dir = os.path.abspath(args.input)
    out_dir = os.path.abspath(args.output)

    if args.overwrite and os.path.isdir(out_dir):
        for f in os.listdir(out_dir):
            fp = os.path.join(out_dir, f)
            if os.path.isfile(fp):
                os.remove(fp)

    ensure_dir(out_dir)

    pages = scan_images(in_dir)
    if not pages:
        print(f"Nenhuma imagem encontrada em {in_dir}.")
        return

    total_chunks = 0
    for p in pages:
        n = slice_image(p, out_dir, args.chunk_height, args.min_height)
        print(f"{os.path.basename(p)} -> {n} faixas")
        total_chunks += n

    print(f"Total de faixas geradas: {total_chunks}")
    print(f"Saída em: {out_dir}")


if __name__ == "__main__":
    main()
