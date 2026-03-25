#!/usr/bin/env bash
set -euo pipefail

if [ ! -d .venv ]; then
    echo "[erro] .venv não encontrado. Execute: make setup"
    exit 1
fi

.venv/bin/pip install --upgrade pip
.venv/bin/pip install -e ".[dev]"
