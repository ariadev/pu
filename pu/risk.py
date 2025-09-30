import re
from typing import Literal, Tuple, List


def analyze_command_risk(command: str) -> Tuple[Literal["low", "medium", "high"], List[str]]:
    reasons: List[str] = []
    normalized = "\n".join(
        line.strip() for line in command.strip().splitlines() if line.strip()
    )
    high_patterns: list[tuple[str, str]] = [
        (r"\brm\s+-rf\s+/(\s|$)", "rm -rf / is catastrophic"),
        (r"\bdd\b[^\n]*\bof=\s*/dev/sd[a-z]\b", "dd to raw disk device"),
        (r"\bmkfs\b", "Filesystem formatting (mkfs)"),
        (r"\b:\(\)\s*\{[^}]*\};\s*:", "Potential fork bomb"),
        (r"\bchown\s+-R\s+root\s+/\b", "Recursive chown of root"),
    ]
    medium_patterns: list[tuple[str, str]] = [
        (r"\brm\b[^\n]*\*(\s|$)", "rm with wildcard could be destructive"),
        (r"\bsudo\s+\brm\b", "sudo rm"),
        (r"curl\b[^\n]*\|\s*(sh|bash)", "Piping remote script to shell"),
        (r">\s*/etc/", "Redirect writing into /etc"),
        (r">\s*/var/", "Redirect writing into /var"),
    ]
    for pattern, msg in high_patterns:
        if re.search(pattern, normalized):
            reasons.append(msg)
    if reasons:
        return "high", reasons
    for pattern, msg in medium_patterns:
        if re.search(pattern, normalized):
            reasons.append(msg)
    if reasons:
        return "medium", reasons
    return "low", []


