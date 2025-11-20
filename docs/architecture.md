# Arquitetura do Projeto

Este documento descreve a arquitetura lógica do pipeline de OCR manuscrito.

## Camadas principais

1. **Dados (`data/`)**
   - `raw/`: insumos brutos (PDFs, fotos).
   - `interim/`: artefatos intermediários (cortes).
   - `pending/`: exemplos a serem anotados.
   - `dataset/`: dataset final em formato (imagem, texto).

2. **Código (`src/`)**
   - `data/`: scripts de preparação de dados.
   - `annotation/`: servidor web e UI de anotação.
   - `models/`: treino, inferência e avaliação (a preencher).
   - `utils/`: utilitários compartilhados.

3. **Experimentação (`notebooks/`)**
   - Exploração inicial, estatísticas e visualizações.

4. **Resultados (`reports/`)**
   - Gráficos, tabelas e relatório final.

5. **Documentação (`docs/`)**
   - Protocolo de anotação, protocolo de treino, resultados.

## Fluxo alto nível

1. Ingestão de dados brutos.
2. Segmentação em linhas/fatias horizontais.
3. Pré-rotulação via OCR.
4. Anotação assistida humana.
5. Split treino/validação.
6. Fine-tuning do modelo.
7. Avaliação (CER/WER) e relatório.
