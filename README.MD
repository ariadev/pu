## pu 🤖 — Natural Language CLI Assistant

pu converts natural language prompts into shell commands. It provides previews, risk checks, and a local history you can inspect or replay.

---

## Installation

Choose one of the recommended methods below.

### Recommended: Web installer (one‑liner)
```bash
curl -fsSL https://raw.githubusercontent.com/ariadev/pu/main/web-install.sh | bash
```
Environment variables:
- `PU_INSTALL_DIR` — target directory for cloning (default: `~/.pu-repo`)
- `PU_AUTO_UPDATE=1` — non-interactive update (skip prompts)

### Recommended: Local installer from a clone
```bash
git clone https://github.com/ariadev/pu.git
cd pu
bash install.sh
# creates .venv, installs openai, and adds /usr/local/bin/pu
```

### Manual: global wrapper (advanced)
```bash
git clone https://github.com/ariadev/pu.git
cd pu
python3 -m pip install -U openai

# install a tiny launcher that keeps the repo on PYTHONPATH
sudo tee /usr/local/bin/pu >/dev/null <<'EOF'
#!/usr/bin/env bash
DIR="/absolute/path/to/your/pu"   # <- replace with your clone path
export PYTHONPATH="$DIR"
exec python3 "$DIR/pu.py" "$@"
EOF
sudo chmod +x /usr/local/bin/pu

# test
pu -p "list large files"
```

### Manual: run directly from the repo
```bash
git clone https://github.com/ariadev/pu.git
cd pu
python3 -m pip install -U openai
./pu.py -p "hello"
```

Optional: use pipx/venv to isolate dependencies if you prefer.

### Uninstall (script-based installs)
```bash
sudo rm -f /usr/local/bin/pu
rm -rf .venv
```

---

## Configuration

First run creates `~/.puconfig`.

Minimal example:
```ini
[openai]
api_key = sk-your-api-key-here
model = gpt-4o-mini

[templates]
# Example macro used with: pu -p ":git-clean"
git-clean = git fetch && git reset --hard origin/main && git clean -fdx
```

Environment variable `OPENAI_API_KEY` is respected on first write.

---

## Usage

Basic:
```bash
pu -p "list large files in the current directory"
```

Dry‑run with previews:
```bash
pu -p "rm -rf build dist" --dry-run
```

File context (depth with ignore and cap):
```bash
pu -p "zip project" --with-files 2 --context-ignore node_modules --context-max 200
```

Choose model and profile:
```bash
pu -p "create tar of txt files" --model gpt-4o-mini --profile safe
```

---

## Subcommands

History (JSONL):
```bash
pu history --last 50
pu history --grep docker
pu history --last 10 --replay 3
```

Doctor (env/config check):
```bash
pu doctor
```

Why (brief explanation):
```bash
pu why            # last
pu why --index 2  # specific
```

Edit (iterate on last/specific command):
```bash
pu edit --instruction "add sudo" --dry-run
pu edit --index 3 --instruction "exclude node_modules"
```

---

## Safety

- Risk checks flag destructive patterns (e.g., `rm -rf /`, `curl | sh`).
- High‑risk commands require double confirmation (type the exact command).
- Medium‑risk shows warnings; in `--profile safe`, an optional challenge can appear.
- Multi‑line commands support per‑line review.

---

## Secrets and Privacy

Secrets are redacted in output and legacy text history. JSONL history retains the raw command locally for replay.

Use `pu history --grep` to search; `--replay` re‑executes with confirmation.

---

## Offline Fallback

If the provider is unavailable, pu falls back to a heuristic generator and logs `provider=heuristic` in history.

---

## Uninstallation

Remove the installed binary:
```bash
sudo rm -f /usr/local/bin/pu
```

Remove local configuration and history (optional):
```bash
rm -f ~/.puconfig ~/.pu_history ~/.pu_history.jsonl
```

If installed in a virtual environment or via pipx:
```bash
# pipx
pipx uninstall pu || true

# venv example
deactivate 2>/dev/null || true
rm -rf path/to/venv
```

If you cloned the repository:
```bash
rm -rf pu
```

---

## Examples

```bash
pu -p ":git-clean"
pu -p "start a python http server on port 8080"
pu -p "docker remove all stopped containers"
```

---

## Troubleshooting

- Run `pu doctor` to validate config and environment.
- If OpenAI is not installed, install with `pip install openai`.
- Use `--dry-run` if unsure; read risk warnings carefully.

 