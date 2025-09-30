import os
import ast
from datetime import datetime
from typing import List
from .constants import HISTORY_PATH, HISTORY_JSONL_PATH
from .redaction import redact_text


def log_history(prompt: str, command: str, executed: bool, risk: str, reasons: List[str], provider: str = "openai"):
    with open(HISTORY_PATH, "a") as f:
        f.write(
            f"[{datetime.now().isoformat()}]\n"
            f"Prompt: {redact_text(prompt)}\n"
            f"Command: {redact_text(command)}\n"
            f"Executed: {executed}\n\n"
        )
    record = {
        "ts": datetime.now().isoformat(),
        "prompt": redact_text(prompt),
        "command": redact_text(command),
        "command_raw": command,
        "executed": executed,
        "risk": risk,
        "reasons": reasons,
        "cwd": os.getcwd(),
        "provider": provider,
    }
    with open(HISTORY_JSONL_PATH, "a") as jf:
        jf.write(f"{record}\n")


def read_history_jsonl() -> List[dict]:
    entries: List[dict] = []
    if not HISTORY_JSONL_PATH.exists():
        return entries
    with open(HISTORY_JSONL_PATH, "r") as jf:
        for line in jf:
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(ast.literal_eval(line))
            except Exception:
                continue
    return entries


