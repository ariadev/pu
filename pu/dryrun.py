import re
from typing import List


def build_dry_run_preview(command: str) -> List[str]:
    previews: List[str] = []
    first_line = command.strip().split("\n", 1)[0].strip()
    m = re.match(r"^rm\s+(.+)$", first_line)
    if m:
        args = m.group(1)
        tokens = [t for t in re.split(r"\s+", args) if t and not re.match(r"^-[-a-zA-Z0-9]+$", t)]
        if tokens:
            targets = " ".join(tokens)
            previews.append(f"Would remove (preview): ls -ld -- {targets}")
        else:
            previews.append("rm arguments not parseable for preview")

    if first_line.startswith("git "):
        if re.search(r"\b(add|commit|restore|rm|mv)\b", first_line):
            previews.append("Suggested: git -c color.ui=always status --short")
        if re.search(r"\b(reset|checkout|switch)\b", first_line):
            previews.append("Suggested: git --no-pager diff --name-status --cached")
        if re.search(r"\bpush\b", first_line):
            previews.append("Suggested: git log --oneline --decorate --graph -20")

    previews.append(f"Trace: set -x; {first_line}")
    return previews


def review_multiline_command(command: str) -> List[str]:
    lines = [ln for ln in (ln.strip() for ln in command.splitlines()) if ln]
    if len(lines) <= 1:
        return lines
    print("This command has multiple lines. Review each line:")
    approved: List[str] = []
    for idx, ln in enumerate(lines, 1):
        print(f"[{idx}] {ln}")
        ans = input("Run this line? [y/N] ").strip().lower()
        if ans == "y":
            approved.append(ln)
    return approved


