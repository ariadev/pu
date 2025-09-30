import argparse
from typing import List, Literal

from .config import load_config
from .provider import generate_command_with_retries
from .commands import execute_command_flow
from .history import read_history_jsonl
from .redaction import redact_text


def run_pu(prompt: str, depth: int | None, dry_run: bool, config, profile: Literal["safe", "standard", "power"] = "standard", context_ignore: List[str] | None = None, context_max_entries: int | None = None):
    # context gathering simplified (moved from monolith for brevity); could import from a context module
    context = ""
    if depth:
        from pathlib import Path
        import fnmatch

        def get_file_tree(path: Path, depth: int, current_level: int = 0, remain: List[int] | None = None) -> str:
            if current_level >= depth:
                return ""
            entries = []
            try:
                children = sorted(path.iterdir())
                for entry in children:
                    if context_ignore and any(fnmatch.fnmatch(entry.name, pat) for pat in context_ignore):
                        continue
                    entries.append("  " * current_level + f"- {entry.name}")
                    if context_max_entries is not None:
                        if remain is None:
                            remain = [context_max_entries]
                        remain[0] -= 1
                        if remain[0] <= 0:
                            break
                    if entry.is_dir():
                        sub = get_file_tree(entry, depth, current_level + 1, remain)
                        if sub:
                            entries.append(sub)
            except PermissionError:
                entries.append("  " * current_level + "- [Permission Denied]")
            return "\n".join(e for e in entries if e)

        context = f"\n\nHere is the file list (depth={depth}):\n{get_file_tree(Path.cwd(), depth, 0, [context_max_entries or 10_000])}\n"

    model = config["openai"].get("model", "gpt-4o-mini")
    api_key = config["openai"]["api_key"]
    command, provider = generate_command_with_retries(prompt, context, model, api_key)
    execute_command_flow(command, dry_run, prompt, provider)


def main():
    parser = argparse.ArgumentParser(description="pu: natural language CLI assistant")
    subparsers = parser.add_subparsers(dest="subcmd")

    parser.add_argument("-p", "--prompt", help="Prompt describing the task")
    parser.add_argument("--with-files", type=int, help="Include file list with given depth")
    parser.add_argument("--context-ignore", action="append", help="Glob to ignore in file context (can repeat)")
    parser.add_argument("--context-max", type=int, help="Max entries to include in file context")
    parser.add_argument("--dry-run", action="store_true", help="Only print the command, do not execute")
    parser.add_argument("--model", help="Override model name for this run")
    parser.add_argument("--profile", choices=["safe", "standard", "power"], default="standard", help="Safety profile")

    p_hist = subparsers.add_parser("history", help="View or replay command history")
    p_hist.add_argument("--last", type=int, default=20, help="Show last N entries (default 20)")
    p_hist.add_argument("--grep", help="Filter entries containing substring")
    p_hist.add_argument("--replay", help="Replay entry by index from the listed set")

    p_doc = subparsers.add_parser("doctor", help="Validate configuration and environment")

    p_why = subparsers.add_parser("why", help="Explain how the last command satisfies its prompt")
    p_why.add_argument("--index", help="Explain a specific history index (default last)")

    p_edit = subparsers.add_parser("edit", help="Modify the last or specified command with an instruction")
    p_edit.add_argument("--index", help="Edit a specific history index (default last)")
    p_edit.add_argument("--instruction", required=True, help="Instruction describing how to modify the command")
    p_edit.add_argument("--dry-run", action="store_true", help="Preview edited command without running")

    args = parser.parse_args()

    from .config import load_config
    config = load_config()

    if args.subcmd == "history":
        from .history import read_history_jsonl

        entries = read_history_jsonl()
        if args.grep:
            q = args.grep.lower()
            entries = [e for e in entries if q in (e.get("prompt", "") + "\n" + e.get("command", "")).lower()]
        entries = entries[-args.last:] if args.last else entries
        if args.replay is not None:
            try:
                index = int(args.replay)
            except ValueError:
                print("❌ --replay expects a numeric index from the listed entries")
                return
            if index < 0 or index >= len(entries):
                print("❌ Replay index out of range")
                return
            entry = entries[index]
            original = entry.get("command_raw") or entry.get("command")
            print(f"About to replay command from {entry.get('ts')}:\n{redact_text(original)}\n")
            confirm = input("Re-run this command? [y/N] ").strip().lower()
            if confirm == "y":
                try:
                    import os, subprocess

                    subprocess.run(original, shell=True, check=True, cwd=entry.get("cwd") or os.getcwd())
                    print("✅ Replayed successfully")
                except subprocess.CalledProcessError as e:
                    print(f"❌ Command failed: {e}")
            return
        for i, e in enumerate(entries):
            print(f"[{i}] {e.get('ts')} :: {e.get('risk','')} :: {e.get('command')}")
        return

    if args.subcmd == "doctor":
        from .cli_doctor import handle_doctor

        handle_doctor(args, config)
        return

    if args.subcmd == "why":
        from .cli_why import handle_why

        handle_why(args, config)
        return

    if args.subcmd == "edit":
        from .cli_edit import handle_edit

        handle_edit(args, config)
        return

    if not args.prompt:
        parser.error("-p/--prompt is required unless using a subcommand")

    if args.model:
        config["openai"]["model"] = args.model

    run_pu(
        args.prompt,
        args.with_files,
        args.dry_run,
        config,
        profile=args.profile,
        context_ignore=args.context_ignore,
        context_max_entries=args.context_max,
    )


