import os
import argparse
from typing import List, Dict

import torch
from PIL import Image
from transformers import TrOCRProcessor, VisionEncoderDecoderModel

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


def main():
    parser = argparse.ArgumentParser(description="Pré-rotular data/pending/img com TrOCR (gera prelabels.json).")
    parser.add_argument("--pending-dir", default="data/pending/img", help="Pasta com recortes pendentes.")
    parser.add_argument("--model", default="microsoft/trocr-base-handwritten",
                        help="Nome do modelo ou caminho local de fine-tune.")
    parser.add_argument("--device", default="auto", choices=["auto", "cpu", "cuda"])
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--max-length", type=int, default=128)
    parser.add_argument("--output", default="prelabels.json", help="Arquivo JSON de saída.")
    args = parser.parse_args()

    pending_dir = os.path.abspath(args.pending_dir)
    files = list_images(pending_dir)
    if not files:
        print(f"Nenhuma imagem encontrada em {pending_dir}")
        return

    if args.device == "auto":
        device = "cuda" if torch.cuda.is_available() else "cpu"
    else:
        device = args.device

    print(f"Carregando modelo {args.model} em {device}...")
    processor = TrOCRProcessor.from_pretrained(args.model)
    model = VisionEncoderDecoderModel.from_pretrained(args.model)
    model.to(device)
    model.eval()

    prelabels: Dict[str, str] = {}

    def batched(seq, bs):
        for i in range(0, len(seq), bs):
            yield seq[i:i+bs]

    with torch.no_grad():
        for batch_files in batched(files, args.batch_size):
            images = []
            for fn in batch_files:
                p = os.path.join(pending_dir, fn)
                img = Image.open(p).convert("L").convert("RGB")
                images.append(img)

            inputs = processor(images=images, return_tensors="pt", padding=True).to(device)
            out = model.generate(**inputs, max_length=args.max_length)
            texts = processor.batch_decode(out, skip_special_tokens=True)

            for fn, t in zip(batch_files, texts):
                prelabels[fn] = t
                print(f"[OCR] {fn} -> {t}")

    import json
    out_path = os.path.abspath(args.output)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(prelabels, f, ensure_ascii=False, indent=2)

    print(f"Salvo {len(prelabels)} prelabels em {out_path}")


if __name__ == "__main__":
    main()
