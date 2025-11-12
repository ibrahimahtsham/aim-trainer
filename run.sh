#!/usr/bin/env bash
set -euo pipefail

# Always operate from script directory
cd "$(dirname "$0")"

# Select python interpreter
if command -v python3 >/dev/null 2>&1; then
  PYTHON=python3
elif command -v python >/dev/null 2>&1; then
  PYTHON=python
else
  echo "Python not found in PATH" >&2
  exit 1
fi

# Create venv if missing
if [ ! -d .venv ]; then
  echo "[+] Creating virtual environment (.venv)"
  "$PYTHON" -m venv .venv
fi

# Activate
# shellcheck source=/dev/null
source .venv/bin/activate

# Upgrade pip (quiet) & install deps
python -m pip install --upgrade pip --quiet
if [ -f requirements.txt ]; then
  echo "[+] Installing requirements"
  python -m pip install -r requirements.txt
fi

# Run the game
exec python main.py "$@"
