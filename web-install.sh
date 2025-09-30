#!/usr/bin/env bash
set -euo pipefail

REPO_URL="https://github.com/ariadev/pu"
DEFAULT_DIR="$HOME/.pu-repo"
WRAPPER_PATH="/usr/local/bin/pu"

echo "[pu] Web installer"

TARGET_DIR="${PU_INSTALL_DIR:-$DEFAULT_DIR}"

if command -v pu >/dev/null 2>&1 || [ -x "$WRAPPER_PATH" ]; then
  echo "[pu] 'pu' already exists at $(command -v pu || echo "$WRAPPER_PATH")"
  read -r -p "Do you want to update/reinstall pu? [y/N] " REPLY || true
  if [[ ! "$REPLY" =~ ^[Yy]$ ]]; then
    echo "[pu] Skipping update. Exiting."
    exit 0
  fi
fi

if [ -d "$TARGET_DIR/.git" ]; then
  echo "[pu] Updating existing repo at $TARGET_DIR"
  git -C "$TARGET_DIR" fetch --all --prune
  git -C "$TARGET_DIR" reset --hard origin/main
else
  echo "[pu] Cloning into $TARGET_DIR"
  rm -rf "$TARGET_DIR"
  git clone "$REPO_URL" "$TARGET_DIR"
fi

echo "[pu] Running installer"
bash "$TARGET_DIR/install.sh"

echo "[pu] Done. Try: pu -p 'hello world'"


