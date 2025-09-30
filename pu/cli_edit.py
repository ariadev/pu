import subprocess
import os
from .history import read_history_jsonl, log_history
from .provider import generate_command_with_retries
from .risk import analyze_command_risk
from .dryrun import build_dry_run_preview, review_multiline_command
from .redaction import redact_text


def handle_edit(args, config):
    entries = read_history_jsonl()
    if not entries:
        print("No history available to edit.")
        return
    entry = entries[-1]
    if args.index is not None:
        try:
            idx = int(args.index)
            if 0 <= idx < len(entries):
                entry = entries[idx]
            else:
                print("Index out of range.")
                return
        except ValueError:
            print("Index must be an integer.")
            return
    base_cmd = entry.get("command_raw") or entry.get("command")
    instruction = args.instruction
    if not instruction:
        print("--instruction is required")
        return
    model = config["openai"].get("model", "gpt-4o-mini")
    api_key = config["openai"]["api_key"]
    modified_prompt = (
        "Modify the following shell command according to the instruction. "
        "Output only the raw modified shell command, no explanations.\n\n"
        f"Command:\n{base_cmd}\n\nInstruction:\n{instruction}\n"
    )
    new_cmd, provider = generate_command_with_retries(modified_prompt, "", model, api_key)
    print(f"\n📝 Edited command:\n{redact_text(new_cmd)}\n")
    executed = False
    risk, reasons = analyze_command_risk(new_cmd)
    if args.dry_run:
        print("💡 Dry run mode: command not executed.")
        if risk != "low":
            print(f"⚠️ Risk: {risk.upper()} — " + "; ".join(reasons))
        for hint in build_dry_run_preview(new_cmd):
            print("👉 " + hint)
    else:
        confirm = input("Run this edited command? [y/N] ").strip().lower()
        if confirm == "y":
            lines_to_run = review_multiline_command(new_cmd)
            if not lines_to_run:
                print("❌ Nothing approved to run.")
            else:
                try:
                    subprocess.run("\n".join(lines_to_run), shell=True, check=True, cwd=os.getcwd())
                    executed = True
                except subprocess.CalledProcessError as e:
                    print(f"❌ Command failed: {e}")
        else:
            print("❌ Cancelled.")
    log_history(f"EDIT: {instruction}", new_cmd, executed, risk, reasons, provider)


