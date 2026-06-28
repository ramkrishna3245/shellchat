import json
import urllib.request
import urllib.error


SYSTEM_PROMPT = """You are a shell command assistant. Your job is to convert natural language into shell commands.

Rules:
- Respond ONLY with valid JSON, no other text.
- The JSON must have keys: "command" (string), "explanation" (string), "safe" (boolean)
- "command": the exact shell command to run
- "explanation": a short friendly explanation of what the command will do
- "safe": true if the command is read-only or safe, false if it can modify/delete data

Examples:
User: "show me all files"
Assistant: {"command": "ls -la", "explanation": "List all files in the current directory", "safe": true}

User: "delete all log files"
Assistant: {"command": "rm *.log", "explanation": "Delete all .log files in the current directory", "safe": false}

User: "find large files over 100MB"
Assistant: {"command": "find . -type f -size +100M", "explanation": "Find all files larger than 100MB", "safe": true}

If the request is not possible or safe, set command to an empty string and explain why."""


def ask_ollama(messages: list[dict], model: str, url: str, timeout: int = 30) -> dict | None:
    payload = {
        "model": model,
        "messages": [{"role": "system", "content": SYSTEM_PROMPT}] + messages,
        "stream": False,
        "options": {"num_predict": 512},
    }
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        f"{url.rstrip('/')}/api/chat",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = json.loads(resp.read().decode())
            content = body.get("message", {}).get("content", "")
            return _parse_response(content)
    except (urllib.error.URLError, json.JSONDecodeError, OSError) as e:
        return {"command": "", "explanation": f"[red]AI Error: {e}[/]", "safe": True}


def ask_openai(messages: list[dict], model: str, api_key: str, base_url: str, timeout: int = 30) -> dict | None:
    if not api_key:
        return {"command": "", "explanation": "[red]API key not configured. Set openai_api_key in ~/.shellchat/config.json[/]", "safe": True}
    payload = {
        "model": model,
        "messages": [{"role": "system", "content": SYSTEM_PROMPT}] + messages,
        "temperature": 0.1,
    }
    data = json.dumps(payload).encode()
    url = f"{base_url.rstrip('/')}/chat/completions"
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = json.loads(resp.read().decode())
            content = body.get("choices", [{}])[0].get("message", {}).get("content", "")
            return _parse_response(content)
    except (urllib.error.URLError, json.JSONDecodeError, OSError) as e:
        return {"command": "", "explanation": f"[red]AI Error: {e}[/]", "safe": True}


def ask(config: dict, messages: list[dict]) -> dict:
    provider = config.get("ai_provider", "ollama")
    timeout = config.get("timeout", 30)

    if provider == "ollama":
        result = ask_ollama(
            messages,
            config.get("model", "llama3.2"),
            config.get("ollama_url", "http://localhost:11434"),
            timeout,
        )
    else:
        result = ask_openai(
            messages,
            config.get("openai_model", "gpt-4o-mini"),
            config.get("openai_api_key", ""),
            config.get("openai_base_url", "https://api.openai.com/v1"),
            timeout,
        )

    if result is None:
        result = {"command": "", "explanation": "[red]AI returned an empty response[/]", "safe": True}
    return result


def _parse_response(content: str) -> dict | None:
    content = content.strip()
    if content.startswith("```"):
        lines = content.splitlines()
        content = "\n".join(lines[1:-1])
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        pass
    start = content.find("{")
    end = content.rfind("}")
    if start != -1 and end != -1:
        try:
            return json.loads(content[start : end + 1])
        except json.JSONDecodeError:
            pass
    return None
