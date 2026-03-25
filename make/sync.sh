#!/usr/bin/env bash
set -euo pipefail

if [ -z "${SYNC_DEST:-}" ]; then
    echo "[erro] Informe SYNC_DEST=user@host:/destino"
    exit 1
fi

rsync ${RSYNC_FLAGS:--av --delete} web/ "$SYNC_DEST"
