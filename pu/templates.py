import configparser
from typing import List


def apply_macros(prompt: str, config: configparser.ConfigParser) -> str:
    templates = config["templates"] if config.has_section("templates") else None
    if not templates:
        return prompt
    p = prompt.strip()
    key = None
    args: List[str] = []
    if p.startswith(":"):
        parts = p[1:].split()
        key = parts[0]
        args = parts[1:]
    elif p in templates:
        key = p
    if key and key in templates:
        raw = templates[key]
        try:
            expanded = raw.format(*args)
        except Exception:
            expanded = raw
        return expanded
    return prompt


