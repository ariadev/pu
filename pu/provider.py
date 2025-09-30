import re
import time
from typing import Tuple
from openai import OpenAI


def heuristic_command_from_prompt(prompt: str) -> str:
    p = prompt.lower().strip()
    if re.search(r"\b(list|show)\b.*\bfiles\b", p):
        return "ls -lh"
    if re.search(r"delete|remove", p) and ".tmp" in p:
        return "rm -i -- *.tmp"
    if "http server" in p or re.search(r"\bserve\b", p):
        m = re.search(r"port\s*(\d+)", p)
        port = m.group(1) if m else "8000"
        return f"python3 -m http.server {port}"
    if "git" in p and "reset" in p and ("origin/main" in p or "origin master" in p or "origin/main" in p):
        return "git fetch && git reset --hard origin/main"
    if "docker" in p and ("remove" in p or "clean" in p) and ("stopped" in p or "dangling" in p):
        return "docker container prune -f && docker image prune -f"
    if "tar" in p or "archive" in p:
        return "tar -czvf archive.tar.gz *.txt"
    return f"echo '{prompt.replace("'", "'\\''")}'"


def generate_command_with_retries(prompt: str, context: str, model: str, api_key: str) -> Tuple[str, str]:
    last_error: str | None = None
    for attempt in range(3):
        try:
            client = OpenAI(api_key=api_key)
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
            command = "\n".join(" ".join(line.split()) for line in command.splitlines())
            return command, "openai"
        except Exception as e:
            last_error = str(e)
            time.sleep(0.5 * (2 ** attempt))
            continue
    fallback = heuristic_command_from_prompt(prompt)
    if last_error:
        print(f"⚠️ Model unavailable, using fallback. Reason: {last_error}")
    return fallback, "heuristic"


