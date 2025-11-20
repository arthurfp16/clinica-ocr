# Handwritten OCR for Clinical Worksheets (HPOCR)

Este repositório contém um pipeline completo, reprodutível e estruturado para
reconhecimento de escrita manual (handwriting OCR) aplicado a formulários e
tabelas de uma clínica.

O projeto implementa:

- Extração automática de faixas horizontais de páginas escaneadas
- Pré-anotação com modelo OCR neural (TrOCR)
- Anotação assistida via interface web (Flask + Tailwind)
- Split organizado (90% treino / 10% validação)
- Base pronta para fine-tuning de modelos de OCR

## Estrutura

```text
data/
  raw/
  interim/slices/
  pending/img/
  discarded/img/
  dataset/
    train/img/
    val/img/

models/
  pretrained/
  fine-tuned/

src/
  data/
  annotation/
  models/
  utils/

notebooks/
reports/
docs/
tests/
```

## Pipeline resumido

1. Coloque as páginas escaneadas em `data/raw/`.
2. Gere faixas horizontais:
   ```bash
   python src/data/prepare_dataset.py --input data/raw --output data/pending/img --chunk-height 50
   ```
3. Gere palpites automáticos (pré-rotulação):
   ```bash
   python src/data/prelabel_pending.py --pending-dir data/pending/img
   ```
4. Rode o servidor de anotação:
   ```bash
   python src/annotation/annotator_server.py
   ```
5. Abra `http://127.0.0.1:8000`, corrija os textos sugeridos e finalize o dataset.
6. Use `data/dataset/train/labels.csv` e `data/dataset/val/labels.csv` no script de treino.

## Reprodutibilidade

- Dependências em `requirements.txt` e `environment.yml`
- Estrutura de pastas estável
- Scripts separados para cada etapa do pipeline

## Licença

MIT.
