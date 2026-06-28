# ShellChat 🐚🤖

**Turn your terminal into an AI-powered chat experience.**

Type what you want in natural language — ShellChat uses AI (Ollama or OpenAI) to suggest and execute shell commands for you.

## Features

- 🤖 **AI-powered** — Describe what you want, AI generates the command
- 💬 **Chat-style TUI** — Beautiful Textual-based interface
- ⚡ **Streaming output** — Real-time command output
- 🎨 **Syntax highlighting** — Rich-colored command output
- 💾 **Session persistence** — Chat history saved across sessions
- ⚙️ **Configurable** — Switch between Ollama (local) and OpenAI
- 🔒 **Safe mode** — Warns before running dangerous commands
- ⌨️ **Command history** — Up/Down arrow navigation

## Quick Start

```bash
pip install -r requirements.txt
python -m shellchat
```

## Usage

### AI Mode (default)
Just type naturally:
```
> show me all files larger than 100MB
```
ShellChat asks AI, shows the command, and runs it.

### Raw Shell
Prefix with `$` to run a command directly:
```
> $ls -la
> $docker ps
```

### Slash Commands

| Command              | Action                     |
|----------------------|----------------------------|
| `:clear`             | Clear chat                 |
| `:help`              | Show help                  |
| `:settings`          | Show current config        |
| `:model <name>`      | Set AI model               |
| `:provider <name>`   | Set provider (ollama/openai) |
| `:exit`              | Quit                       |

### Keyboard

| Key      | Action           |
|----------|------------------|
| Enter    | Send message     |
| Up/Down  | Command history  |
| Ctrl+L   | Clear chat       |
| Esc      | Cancel           |

## Configuration

Edit `~/.shellchat/config.json`:

```json
{
  "ai_provider": "ollama",
  "model": "llama3.2",
  "ollama_url": "http://localhost:11434",
  "openai_api_key": "",
  "openai_model": "gpt-4o-mini",
  "auto_execute": true,
  "safe_mode": true,
  "timeout": 60
}
```

### AI Providers

**Ollama** (default, free & local):
```bash
ollama pull llama3.2
```

**OpenAI**:
Set `"ai_provider": "openai"` and add your `openai_api_key`.
