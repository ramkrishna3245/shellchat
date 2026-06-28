import json
import os
from pathlib import Path


CONFIG_DIR = Path.home() / ".shellchat"
CONFIG_FILE = CONFIG_DIR / "config.json"
HISTORY_FILE = CONFIG_DIR / "history.json"

DEFAULT_CONFIG = {
    "ai_provider": "ollama",
    "model": "llama3.2",
    "ollama_url": "http://localhost:11434",
    "openai_api_key": "",
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
