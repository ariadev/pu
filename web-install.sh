#!/usr/bin/env bash
set -euo pipefail

REPO_URL="https://github.com/ariadev/pu"
DEFAULT_DIR="$HOME/.pu-repo"
WRAPPER_PATH="/usr/local/bin/pu"

echo "[pu] Web installer"

TARGET_DIR="${PU_INSTALL_DIR:-$DEFAULT_DIR}"

ASK_UPDATE() {
  local prompt_msg=${1:-"Do you want to update/reinstall pu? [y/N] "}
  if [ "${PU_AUTO_UPDATE:-}" = "1" ]; then
    return 0
  fi
  if [ -t 0 ]; then
    read -r -p "$prompt_msg" REPLY || true
    [[ "$REPLY" =~ ^[Yy]$ ]]
    return
  else
    echo "[pu] Non-interactive session and PU_AUTO_UPDATE not set; skipping update." >&2
    return 1
  fi
}

if command -v pu >/dev/null 2>&1 || [ -x "$WRAPPER_PATH" ]; then
  echo "[pu] 'pu' already exists at $(command -v pu || echo \"$WRAPPER_PATH\")"
  if ! ASK_UPDATE; then
    echo "[pu] Skipping update. Exiting."
    exit 0
  fi
fi

if [ -d "$TARGET_DIR/.git" ]; then
  echo "[pu] Repo already present at $TARGET_DIR"
  if ASK_UPDATE "Update existing repo at $TARGET_DIR? [y/N] "; then
    echo "[pu] Updating $TARGET_DIR"
    git -C "$TARGET_DIR" fetch --all --prune
    git -C "$TARGET_DIR" reset --hard origin/main
  else
    echo "[pu] Leaving repo as-is. Proceeding to run installer."
  fi
else
  echo "[pu] Cloning into $TARGET_DIR"
  rm -rf "$TARGET_DIR"
  git clone "$REPO_URL" "$TARGET_DIR"
fi

echo "[pu] Running installer"
bash "$TARGET_DIR/install.sh"

echo "[pu] Done. Try: pu -p 'hello world'"


