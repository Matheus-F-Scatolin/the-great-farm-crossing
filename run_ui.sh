#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
if [ -d .venv/bin ]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
elif [ -d .venv/Scripts ]; then
  # shellcheck disable=SC1091
  source .venv/Scripts/activate
fi
# Detecta se 'python3' ou 'python' está disponível
if command -v python3 >/dev/null 2>&1; then
  PYTHON_CMD="python3"
elif command -v python >/dev/null 2>&1; then
  PYTHON_CMD="python"
else
  echo "Erro: Python não foi encontrado no PATH." >&2
  exit 1
fi

exec "$PYTHON_CMD" -m ui.main "$@"
