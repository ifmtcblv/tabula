# Tabula – Painel de Dados do SUAP

Lê o export oficial do SUAP (`data/master.xls`), gera agregados em CSV e publica um painel estático com gráficos (Chart.js). Desenvolvido para o **IFMT (Instituto Federal de Mato Grosso)**.

## Fluxo local

1. Instale dependências (cria `.venv` se necessário):
   ```bash
   make setup
   ```
2. Coloque o arquivo exportado do SUAP em `data/master.xls`.
3. Gere o site e os datasets (salvos em `web/datasets/`):
   ```bash
   make build
   ```
4. Rode o servidor estático localmente:
   ```bash
   make run
   # abre http://localhost:8000
   ```

> `make build` aciona `run/construir_datasets.py` (pandas + xlrd/openpyxl) e só emite os CSVs cujas colunas existirem na planilha.

## Publicação no servidor

1. **(Opcional)** Crie as pastas para datasets e web (ex.: `/opt/suap`):
   ```bash
   sudo mkdir -p /opt/suap/web
   sudo mkdir -p /opt/suap/web/datasets
   sudo chown -R $USER /opt/suap
   ```
2. Sincronize os arquivos gerados localmente (usa o target `sync-web` que já chama `rsync`):
   ```bash
   make sync-web SYNC_DEST=user@servidor:/opt/suap/web/
   # opcional: altere RSYNC_FLAGS=-av --delete (default)
   ```
   > O container publicado traz apenas um `index.html` placeholder. Publique o conteúdo de `web/` para que o painel fique disponível.
3. No servidor, rode o container apontando para as pastas publicadas (monte apenas o que precisar):
   ```bash
   docker run --rm -d \
     -e PORT=8000 \
     -e DATA_INPUT=/data/master.xls \
     -e DATA_OUTPUT=/app/web/datasets \
     -p 8000:8000 \
     -v /opt/suap/web:/app/web \
     carlosrabelo/tabula:TAG
   ```
   - Adicione `-v /opt/suap/data:/data:ro` se quiser montar o `master.xls` para regerar os CSVs.
   - `make docker-run` monta os volumes indicados por `HOST_DATA_DIR` e `HOST_DATASETS_DIR`. Se deixá-los vazios (default local), nenhum volume é passado, evitando o erro de bind com caminho vazio.

## Datasets gerados (quando os campos existem em `master.xls`)

**Visão geral**
- `alunos_por_situacao.csv`
- `modalidade.csv`
- `dist_percentual_progresso.csv`
- `turno.csv`

**Inclusão & Acesso**
- `forma_ingresso.csv`
- `cota_mec.csv` / `cota_sistec.csv` / `cotas.csv`
- `etnia_raca.csv`
- `necessidades_especiais.csv`
- `tipo_escola_origem.csv`
- `natureza_participacao.csv`
- `transporte_tipo.csv`

**Análises cruzadas**
- `natureza_escola.csv` — Natureza de Participação × Tipo de Escola de Origem
- `situacao_escola.csv` — Situação × Tipo de Escola de Origem
- `campus_natureza.csv` — Campus × Natureza de Participação
- `natureza_turno.csv` — Natureza de Participação × Turno
- `natureza_situacao.csv` — Natureza de Participação × Situação
- `natureza_coorte.csv` — Evolução de matrículas por Natureza de Participação ao longo dos anos

**Metadados**
- `meta.json` — data/hora da última importação (exibida no rodapé do painel)

> Colunas ausentes são ignoradas e o dataset correspondente não é criado.

## Estrutura principal

- `data/`: arquivo fonte exportado do SUAP (`master.xls`).
- `run/construir_datasets.py`: normaliza nomes de colunas (case/acento), trata datas/percentuais, gera os agregados em `web/datasets/` e registra a data de importação em `web/datasets/meta.json`.
- `run/gerar_site.py`: copia estáticos e gera o `web/index.html`.
- `src/`: módulos Python (construtores de datasets, utilitários, templates).
- `web/`: HTML/CSS/JS (Chart.js) consumindo os CSVs via `fetch`.
- `Dockerfile`: imagem enxuta que serve `web/` e tenta regerar os CSVs em runtime se `DATA_INPUT` estiver disponível.
