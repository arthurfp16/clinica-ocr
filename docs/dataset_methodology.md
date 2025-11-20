# Metodologia de Construção do Dataset

## Objetivo

Construir um dataset de linhas manuscritas em formulários clínicos, com foco
na caligrafia dos colaboradores e beneficiarios e em contexto de tabelas.

## Processo

1. **Coleta**
   - Digitalizar as páginas físicas com resolução consistente.
   - Armazenar arquivos em `data/raw/`.

2. **Segmentação em linhas**
   - Usar `prepare_dataset.py` para cortar as páginas em faixas horizontais
     de ~50px, cobrindo a largura total da página.
   - Cada faixa é salva em `data/pending/img/`.

3. **Pré-rotulação automática**
   - Usar `prelabel_pending.py` para rodar o modelo pós-treinado (u TrOCR sem pós treinamento para cenario inicial ) afim de gerar palpites afim de facilitar processo de rotulação.
   - As saídas são salvas em `prelabels.json` na raiz do projeto.

4. **Anotação assistida**
   - O servidor Flask lê `data/pending/img/` e `prelabels.json`.
   - A UI exibe a imagem, preenche o campo de texto com o chute do modelo,
     e o anotador apenas corrige.

5. **Split treino/validação**
   - Após anotar tudo, o endpoint `/api/finalize` é chamado.
   - O script cria:
     - `data/dataset/train/labels.csv`
     - `data/dataset/val/labels.csv`
   - E move 10% das imagens para `data/dataset/val/img/`.

## Formato das labels

CSV com colunas:

- `image_path`: caminho relativo, ex. `img/arquivo.png`
- `text`: transcrição exata do conteúdo da imagem.

## Boas práticas ao Anotar

- Manter consistência de ortografia.
- Preservar acentos e caracteres especiais.
- Substituir texto ilegível por um token especial, se desejado (ex.: `<illegível>`).
