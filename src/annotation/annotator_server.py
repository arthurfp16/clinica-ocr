import os
import csv
import json
import random
import shutil
from typing import List, Dict

from flask import Flask, jsonify, request, send_from_directory, send_file

# Diretórios base
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(os.path.dirname(THIS_DIR))

DATA_DIR = os.path.join(ROOT_DIR, "data")
PENDING_IMG_DIR = os.path.join(DATA_DIR, "pending", "img")
TRAIN_IMG_DIR = os.path.join(DATA_DIR, "dataset", "train", "img")
VAL_IMG_DIR = os.path.join(DATA_DIR, "dataset", "val", "img")
DISCARD_IMG_DIR = os.path.join(DATA_DIR, "discarded", "img")

TRAIN_LABELS_RAW = os.path.join(DATA_DIR, "dataset", "train", "labels_raw.csv")
TRAIN_LABELS = os.path.join(DATA_DIR, "dataset", "train", "labels.csv")
VAL_LABELS = os.path.join(DATA_DIR, "dataset", "val", "labels.csv")

INDEX_HTML = os.path.join(THIS_DIR, "index.html")

PRELABELS_PATH = os.path.join(ROOT_DIR, "prelabels.json")
PRELABELS: Dict[str, str] = {}


def ensure_dirs():
    for d in [
        PENDING_IMG_DIR,
        TRAIN_IMG_DIR,
        VAL_IMG_DIR,
        DISCARD_IMG_DIR,
        os.path.dirname(TRAIN_LABELS_RAW),
        os.path.dirname(TRAIN_LABELS),
        os.path.dirname(VAL_LABELS),
    ]:
        os.makedirs(d, exist_ok=True)


def load_prelabels():
    global PRELABELS
    if os.path.isfile(PRELABELS_PATH):
        try:
            with open(PRELABELS_PATH, "r", encoding="utf-8") as f:
                PRELABELS = json.load(f)
            print(f"[prelabels] Carregado {len(PRELABELS)} sugestões de OCR.")
        except Exception as e:
            print(f"[prelabels] ERRO ao carregar {PRELABELS_PATH}: {e}")
            PRELABELS = {}
    else:
        print("[prelabels] Nenhum prelabels.json encontrado.")
        PRELABELS = {}


def list_images(dir_path: str) -> List[str]:
    if not os.path.isdir(dir_path):
        return []
    files = [
        f for f in os.listdir(dir_path)
        if os.path.isfile(os.path.join(dir_path, f))
        and os.path.splitext(f.lower())[1] in [".png", ".jpg", ".jpeg", ".bmp", ".webp", ".tif", ".tiff"]
    ]
    files.sort()
    return files


def append_label_raw(filename: str, text: str) -> None:
    header_needed = not os.path.exists(TRAIN_LABELS_RAW)
    with open(TRAIN_LABELS_RAW, "a", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        if header_needed:
            writer.writerow(["image_path", "text"])
        writer.writerow([f"img/{filename}", text])


app = Flask(__name__)


@app.route("/")
def index():
    if os.path.isfile(INDEX_HTML):
        return send_file(INDEX_HTML)
    return "<h1>index.html não encontrado</h1>", 404


@app.route("/image/<path:filename>")
def serve_image(filename: str):
    return send_from_directory(PENDING_IMG_DIR, filename)


@app.route("/api/next", methods=["GET"])
def api_next():
    ensure_dirs()
    pending_files = list_images(PENDING_IMG_DIR)

    if not pending_files:
        train_files = list_images(TRAIN_IMG_DIR)
        discard_files = list_images(DISCARD_IMG_DIR)
        total = len(train_files) + len(discard_files)
        return jsonify({
            "done": True,
            "message": "Nenhuma imagem pendente.",
            "remaining": 0,
            "total": total,
            "suggestion": ""
        })

    filename = pending_files[0]
    train_files = list_images(TRAIN_IMG_DIR)
    discard_files = list_images(DISCARD_IMG_DIR)
    total = len(pending_files) + len(train_files) + len(discard_files)
    processed = total - len(pending_files)
    suggestion = PRELABELS.get(filename, "")

    return jsonify({
        "done": False,
        "filename": filename,
        "url": f"/image/{filename}",
        "remaining": len(pending_files),
        "processed": processed,
        "total": total,
        "suggestion": suggestion,
    })


@app.route("/api/save", methods=["POST"])
def api_save():
    data = request.get_json(force=True)
    filename = data.get("filename")
    text = (data.get("text") or "").strip()

    if not filename or not text:
        return jsonify({"ok": False, "error": "filename e text são obrigatórios"}), 400

    src = os.path.join(PENDING_IMG_DIR, filename)
    if not os.path.isfile(src):
        return jsonify({"ok": False, "error": "arquivo não encontrado"}), 404

    dst = os.path.join(TRAIN_IMG_DIR, filename)
    shutil.move(src, dst)
    append_label_raw(filename, text)
    return jsonify({"ok": True})


@app.route("/api/discard", methods=["POST"])
def api_discard():
    data = request.get_json(force=True)
    filename = data.get("filename")

    if not filename:
        return jsonify({"ok": False, "error": "filename é obrigatório"}), 400

    src = os.path.join(PENDING_IMG_DIR, filename)
    if not os.path.isfile(src):
        return jsonify({"ok": False, "error": "arquivo não encontrado"}), 404

    dst = os.path.join(DISCARD_IMG_DIR, filename)
    shutil.move(src, dst)
    return jsonify({"ok": True})


@app.route("/api/finalize", methods=["POST"])
def api_finalize():
    ensure_dirs()

    if not os.path.isfile(TRAIN_LABELS_RAW):
        return jsonify({"ok": False, "error": "Nenhum labels_raw encontrado"}), 400

    rows = []
    with open(TRAIN_LABELS_RAW, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for r in reader:
            if r.get("image_path") and r.get("text"):
                rows.append(r)

    if len(rows) < 2:
        return jsonify({"ok": False, "error": "Poucos exemplos"}), 400

    random.shuffle(rows)
    n_total = len(rows)
    n_train = max(1, int(n_total * 0.90))
    n_val = n_total - n_train

    train_rows = rows[:n_train]
    val_rows = rows[n_train:]

    with open(TRAIN_LABELS, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, ["image_path", "text"])
        writer.writeheader()
        writer.writerows(train_rows)

    with open(VAL_LABELS, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, ["image_path", "text"])
        writer.writeheader()
        writer.writerows(val_rows)

    for r in val_rows:
        filename = os.path.basename(r["image_path"])
        src = os.path.join(TRAIN_IMG_DIR, filename)
        dst = os.path.join(VAL_IMG_DIR, filename)
        if os.path.isfile(src):
            shutil.move(src, dst)

    return jsonify({
        "ok": True,
        "total": n_total,
        "train_count": n_train,
        "val_count": n_val,
        "train_labels": os.path.relpath(TRAIN_LABELS, ROOT_DIR).replace("\", "/"),
        "val_labels": os.path.relpath(VAL_LABELS, ROOT_DIR).replace("\", "/"),
    })


if __name__ == "__main__":
    ensure_dirs()
    load_prelabels()
    print("Servidor rodando em http://127.0.0.1:8000")
    app.run(host="127.0.0.1", port=8000, debug=True)
