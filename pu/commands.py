import os
import subprocess
from typing import List, Literal

from .redaction import redact_text
from .risk import analyze_command_risk
from .dryrun import build_dry_run_preview, review_multiline_command
from .history import log_history


def execute_command_flow(command: str, dry_run: bool, prompt: str, provider: str) -> None:
    redacted_command = redact_text(command)
    print(f"\n📝 Command generated:\n{redacted_command}\n")

    executed = False
    risk, reasons = analyze_command_risk(command)

    if dry_run:
        print("💡 Dry run mode: command not executed.")
        if risk != "low":
            print(f"⚠️ Risk: {risk.upper()} — " + "; ".join(reasons))
        for hint in build_dry_run_preview(command):
            print("👉 " + hint)
    else:
        if risk == "high":
            print(f"⚠️ This command appears HIGH RISK: " + "; ".join(reasons))
            first = input("Proceed anyway? [y/N] ").strip().lower()
            if first == "y":
                challenge = input("Type the exact command to confirm: \n> ").strip()
                if challenge != command.strip():
                    print("❌ Confirmation did not match. Cancelled.")
                else:
                    lines_to_run = review_multiline_command(command)
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
        else:
            if risk == "medium":
                print(f"⚠️ Risk: MEDIUM — " + "; ".join(reasons))
            confirm = input("Run this command? [y/N] ").strip().lower()
            if confirm == "y":
                lines_to_run = review_multiline_command(command)
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

    log_history(prompt, command, executed, risk, reasons, provider)


