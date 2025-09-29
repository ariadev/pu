#!/usr/bin/env python3
import argparse
import subprocess
import os
import re
import configparser
from pathlib import Path
from datetime import datetime
from openai import OpenAI

CONFIG_PATH = Path.home() / ".puconfig"
HISTORY_PATH = Path.home() / ".pu_history"


def load_config():
    """Load config from ~/.puconfig"""
    config = configparser.ConfigParser()
    if CONFIG_PATH.exists():
        config.read(CONFIG_PATH)
    else:
        # Create a default config file if not exists
        config["openai"] = {
            "api_key": os.environ.get("OPENAI_API_KEY", "your_api_key_here"),
            "model": "gpt-4o-mini",
        }
        with open(CONFIG_PATH, "w") as f:
            config.write(f)
    return config


def log_history(prompt, command, executed):
    """Append to ~/.pu_history"""
    with open(HISTORY_PATH, "a") as f:
        f.write(
            f"[{datetime.now().isoformat()}]\n"
            f"Prompt: {prompt}\n"
            f"Command: {command}\n"
            f"Executed: {executed}\n\n"
        )


def run_pu(prompt: str, depth: int | None, dry_run: bool, config):
    client = OpenAI(api_key=config["openai"]["api_key"])
    model = config["openai"].get("model", "gpt-4o-mini")

    context = ""
    if depth:
        from pathlib import Path

        def get_file_tree(path: Path, depth: int, current_level: int = 0) -> str:
            if current_level >= depth:
                return ""
            entries = []
            try:
                for entry in sorted(path.iterdir()):
                    entries.append("  " * current_level + f"- {entry.name}")
                    if entry.is_dir():
                        entries.append(get_file_tree(entry, depth, current_level + 1))
            except PermissionError:
                entries.append("  " * current_level + "- [Permission Denied]")
            return "\n".join(e for e in entries if e)

        context = f"\n\nHere is the file list (depth={depth}):\n{get_file_tree(Path.cwd(), depth)}\n"

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a helpful CLI assistant. "
                    "Output only the raw shell command, without explanations, without markdown, without code fences."
                ),
            },
            {"role": "user", "content": prompt + context},
        ],
    )

    command = response.choices[0].message.content.strip()
    command = re.sub(r"^```[a-zA-Z]*\n?|```$", "", command).strip()

    print(f"\n📝 Command generated:\n{command}\n")

    executed = False
    if dry_run:
        print("💡 Dry run mode: command not executed.")
    else:
        confirm = input("Run this command? [y/N] ").strip().lower()
        if confirm == "y":
            try:
                subprocess.run(command, shell=True, check=True, cwd=os.getcwd())
                executed = True
            except subprocess.CalledProcessError as e:
                print(f"❌ Command failed: {e}")
        else:
            print("❌ Cancelled.")

    # Log to history
    log_history(prompt, command, executed)


def main():
    parser = argparse.ArgumentParser(description="pu: natural language CLI assistant")
    parser.add_argument("-p", "--prompt", required=True, help="Prompt describing the task")
    parser.add_argument("--with-files", type=int, help="Include file list with given depth")
    parser.add_argument("--dry-run", action="store_true", help="Only print the command, do not execute")
    args = parser.parse_args()

    config = load_config()
    run_pu(args.prompt, args.with_files, args.dry_run, config)


if __name__ == "__main__":
    main()
