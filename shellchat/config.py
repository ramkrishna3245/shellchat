import json
import os
from pathlib import Path


CONFIG_DIR = Path.home() / ".shellchat"
CONFIG_FILE = CONFIG_DIR / "config.json"
HISTORY_FILE = CONFIG_DIR / "history.json"

# Pre-configured providers (any OpenAI-compatible API also works via "openai" provider)
PROVIDERS = {
    "ollama": {
        "label": "Ollama (local)",
        "model": "llama3.2",
        "openai_base_url": "",
    },
    "openai": {
        "label": "OpenAI",
        "model": "gpt-4o-mini",
        "openai_base_url": "https://api.openai.com/v1",
    },
    "groq": {
        "label": "Groq",
        "model": "llama-3.3-70b-versatile",
        "openai_base_url": "https://api.groq.com/openai/v1",
    },
    "together": {
        "label": "Together AI",
        "model": "mistralai/Mixtral-8x22B-Instruct-v0.1",
        "openai_base_url": "https://api.together.xyz/v1",
    },
    "deepseek": {
        "label": "DeepSeek",
        "model": "deepseek-chat",
        "openai_base_url": "https://api.deepseek.com/v1",
    },
    "perplexity": {
        "label": "Perplexity",
        "model": "sonar-pro",
        "openai_base_url": "https://api.perplexity.ai",
    },
}

DEFAULT_CONFIG = {
    "ai_provider": "ollama",
    "model": "llama3.2",
    "ollama_url": "http://localhost:11434",
    "openai_api_key": "",
    "openai_base_url": "https://api.openai.com/v1",
    "openai_model": "gpt-4o-mini",
    "history_file": str(HISTORY_FILE),
    "auto_execute": True,
    "safe_mode": True,
    "timeout": 60,
}


def load() -> dict:
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE) as f:
                return {**DEFAULT_CONFIG, **json.load(f)}
        except (json.JSONDecodeError, OSError):
            pass
    return dict(DEFAULT_CONFIG)


def save(cfg: dict) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f, indent=2)


def save_history(entries: list[dict]) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(HISTORY_FILE, "w") as f:
        json.dump(entries[-200:], f, indent=2)


def load_history() -> list[dict]:
    if HISTORY_FILE.exists():
        try:
            with open(HISTORY_FILE) as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return []
