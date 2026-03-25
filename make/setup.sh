#!/usr/bin/env bash
set -euo pipefail

if [ ! -d .venv ]; then
    echo "[setup] Criando ambiente virtual..."
    python3 -m venv .venv
fi

echo "[setup] Instalando dependências..."
.venv/bin/pip install --upgrade pip --quiet
.venv/bin/pip install -e ".[dev]" --quiet
echo "[setup] Pronto."
