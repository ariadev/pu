from typing import List

from .provider import generate_command_with_retries


def handle_doctor(args, config):
    print("pu doctor — environment check")
    problems: List[str] = []
    import sys
    pyver = sys.version.split()[0]
    print(f"Python: {pyver}")
    api_key = config.get("openai", {}).get("api_key")
    model = config.get("openai", {}).get("model")
    if not api_key or api_key == "your_api_key_here":
        problems.append("OpenAI API key missing or placeholder in ~/.puconfig or env")
    else:
        print("OpenAI API key: present (redacted)")
    print(f"Model: {model or 'not set'}")
    try:
        cmd, provider = generate_command_with_retries("list files", "", model or "gpt-4o-mini", api_key or "")
        print(f"Model check: OK via {provider}")
    except Exception as e:
        problems.append(f"Model check failed: {e}")
    for tool in ["git", "docker", "tar"]:
        from shutil import which
        if which(tool):
            print(f"{tool}: found")
        else:
            print(f"{tool}: not found (optional)")
    if problems:
        print("\n❌ Issues detected:")
        for p in problems:
            print(" - " + p)
        print("\nTips: set OPENAI_API_KEY, edit ~/.puconfig, or run in --dry-run.")
    else:
        print("\n✅ All checks passed")


