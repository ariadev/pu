from openai import OpenAI
from .history import read_history_jsonl


def handle_why(args, config):
    entries = read_history_jsonl()
    if not entries:
        print("No history available.")
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
    prompt = entry.get("prompt", "")
    command = entry.get("command_raw") or entry.get("command")
    model = config["openai"].get("model", "gpt-4o-mini")
    api_key = config["openai"]["api_key"]
    try:
        client = OpenAI(api_key=api_key)
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "Explain briefly in 3-5 bullets how the given shell command satisfies the user's prompt. Be concise."},
                {"role": "user", "content": f"Prompt: {prompt}\nCommand: {command}"},
            ],
        )
        explanation = resp.choices[0].message.content.strip()
        print(explanation)
    except Exception as e:
        print(f"Failed to get explanation: {e}")


