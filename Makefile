MAKEFLAGS += --no-print-directory

.DEFAULT_GOAL := help

SHELL := /usr/bin/env bash

-include .env
export

.PHONY: build clean datasets docker-build docker-push docker-run docker-shell docker-tag fmt help install lint quality run setup site sync-web test typecheck

PORT               ?= 8000
DATA_INPUT         ?= data/master.xls
DATA_OUTPUT        ?= web/datasets
BUILD_SCRIPT       := run/construir_datasets.py
SITE_SCRIPT        := run/gerar_site.py
IMAGE              ?= ifmtcblv/tabula
TAG                ?= $(shell git describe --tags --always --dirty 2>/dev/null || echo latest)
FULL               := $(IMAGE):$(TAG)
LATEST             := $(IMAGE):latest
DOCKER             ?= docker
HOST_DATA_DIR      ?=
HOST_DATASETS_DIR  ?=
SYNC_DEST          ?=
RSYNC_FLAGS        ?= -av --delete
DOCKER_DATA_VOLUME     := $(if $(HOST_DATA_DIR),-v $(HOST_DATA_DIR):/data:ro,)
DOCKER_DATASETS_VOLUME := $(if $(HOST_DATASETS_DIR),-v $(HOST_DATASETS_DIR):/app/web/datasets,)

help: ## Exibe os targets disponíveis
	@echo "tabula - Targets disponíveis"
	@echo ""
	@grep -hE '^[a-zA-Z_-]+:.*## ' $(MAKEFILE_LIST) \
		| sort \
		| awk 'BEGIN {FS = ":.*## "} {printf "  %-18s %s\n", $$1, $$2}'

setup: ## Cria .venv e instala dependências
	@./make/setup.sh

install: ## Instala dependências no .venv existente
	@./make/install.sh

site: ## Regenera web/ (copia estáticos e gera index.html)
	@.venv/bin/python ./$(SITE_SCRIPT)

datasets: site ## Processa $(DATA_INPUT) e gera CSVs em $(DATA_OUTPUT)
	@.venv/bin/python ./$(BUILD_SCRIPT) --in $(DATA_INPUT) --out $(DATA_OUTPUT)

build: datasets ## Executa site e datasets

run: datasets ## Serve o dashboard em http://localhost:$(PORT)
	@echo "Servindo web/ em http://localhost:$(PORT)"
	@.venv/bin/python -m http.server $(PORT) --directory web

fmt: ## Formata fontes Python com ruff
	@.venv/bin/ruff format .

lint: ## Verifica fontes Python com ruff
	@.venv/bin/ruff check .

typecheck: ## Verifica tipos com mypy
	@.venv/bin/mypy .

quality: fmt lint typecheck ## Executa todas as verificações de qualidade

test: ## Executa os testes com pytest
	@./make/test.sh

docker-build: ## Builda a imagem $(FULL)
	@$(DOCKER) build --build-arg PORT=$(PORT) -t $(FULL) .

docker-tag: ## Cria tag latest para a imagem
	@$(DOCKER) tag $(FULL) $(LATEST)

docker-push: docker-build docker-tag ## Envia a imagem para o registry
	@$(DOCKER) push $(FULL)

docker-run: ## Executa a imagem expondo a porta $(PORT)
	@$(DOCKER) run --rm -it \
		-e PORT=$(PORT) \
		-e DATA_INPUT=/data/master.xls \
		-e DATA_OUTPUT=/app/web/datasets \
		-p $(PORT):$(PORT) \
		$(DOCKER_DATA_VOLUME) \
		$(DOCKER_DATASETS_VOLUME) \
		$(FULL)

docker-shell: ## Abre um shell na imagem
	@$(DOCKER) run --rm -it \
		$(DOCKER_DATA_VOLUME) \
		$(DOCKER_DATASETS_VOLUME) \
		$(FULL) /bin/bash

sync-web: ## Publica web/ no destino configurado em SYNC_DEST
	@./make/sync.sh

clean: ## Remove datasets gerados e caches Python
	@find web/ -mindepth 1 ! -name '.gitkeep' -delete
	@find . -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
