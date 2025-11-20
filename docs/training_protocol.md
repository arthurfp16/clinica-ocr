# Protocolo de Treinamento

Este arquivo descreve um protocolo recomendável para fine-tuning de um modelo
TrOCR (ou similar) usando o dataset gerado.

## Modelo de base

- `microsoft/trocr-base-handwritten` (ou variante apropriada).

## Entradas

- `data/dataset/train/labels.csv`
- `data/dataset/val/labels.csv`

## Pré-processamento

- Normalizar tamanho da imagem (ex.: resize proporcional e pad).
- Converter para escala de cinza ou manter RGB, conforme o modelo.
- Aplicar normalização padrão do ViT (caso TrOCR).

## Hiperparâmetros sugeridos (exemplo)

- Batch size: 8–16 (dependendo da GPU).
- Épocas: 10–50, monitorando CER/ WER em validação.
- Otimizador: AdamW, LR ~ 5e-5.
- Esquema de LR: linear com warmup opcional.

## Métricas

- CER (Character Error Rate)
- WER (Word Error Rate)

## Reprodutibilidade

- Fixar semente aleatória (`seed`).
- Versões de libs registradas (via `requirements.txt`).
