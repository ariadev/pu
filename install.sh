#!/usr/bin/env bash
set -euo pipefail

# Install pu globally by creating a repo-local virtualenv and a wrapper at /usr/local/bin/pu

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
WRAPPER_PATH="/usr/local/bin/pu"
VENV_DIR="$ROOT_DIR/.venv"

echo "[pu] Installing into virtualenv at: $VENV_DIR"

if ! command -v python3 >/dev/null 2>&1; then
  echo "[pu] ERROR: python3 not found in PATH." >&2
  exit 1
fi

PYTHON="python3"

# Create venv if missing
if [ ! -d "$VENV_DIR" ]; then
  "$PYTHON" -m venv "$VENV_DIR"
fi

"$VENV_DIR/bin/python" -m pip install --upgrade pip setuptools wheel >/dev/null
"$VENV_DIR/bin/python" -m pip install --upgrade openai

echo "[pu] Creating wrapper at $WRAPPER_PATH"

# Choose tee with sudo only if needed
TEE="tee"
if [ ! -w "$(dirname "$WRAPPER_PATH")" ]; then
  if command -v sudo >/dev/null 2>&1; then
    TEE="sudo tee"
  else
    echo "[pu] ERROR: Cannot write to $(dirname "$WRAPPER_PATH"). Re-run with sudo or grant permissions." >&2
    exit 1
  fi
fi

cat <<'EOF' | $TEE "$WRAPPER_PATH" >/dev/null
#!/usr/bin/env bash
DIR="$ROOT_DIR"
exec "$DIR/.venv/bin/python" "$DIR/pu.py" "$@"
EOF

chmod +x "$WRAPPER_PATH" 2>/dev/null || sudo chmod +x "$WRAPPER_PATH"

echo "[pu] Installed wrapper: $WRAPPER_PATH"
echo "[pu] Test: pu -p 'hello world'"
echo "[pu] If 'openai' is not configured yet, run: pu doctor"


