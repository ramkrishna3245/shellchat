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
  "openai_base_url": "https://api.openai.com/v1",
  "openai_model": "gpt-4o-mini",
  "auto_execute": true,
  "safe_mode": true,
  "timeout": 60
}
```

### AI Providers

ShellChat supports **any OpenAI-compatible API** and **Ollama**.

#### Built-in providers (set `ai_provider` to one of these):

| Provider     | Default Model                        | API Base URL                        |
|-------------|--------------------------------------|-------------------------------------|
| `ollama`    | `llama3.2`                           | http://localhost:11434              |
| `openai`    | `gpt-4o-mini`                        | https://api.openai.com/v1           |
| `groq`      | `llama-3.3-70b-versatile`            | https://api.groq.com/openai/v1     |
| `together`  | `mistralai/Mixtral-8x22B-Instruct-v0.1` | https://api.together.xyz/v1    |
| `deepseek`  | `deepseek-chat`                      | https://api.deepseek.com/v1        |
| `perplexity`| `sonar-pro`                          | https://api.perplexity.ai          |

#### Use **any** OpenAI-compatible API:

Set `"ai_provider": "openai"`, then change `openai_base_url` and `openai_model` to match your provider. This works with any API that has a `/v1/chat/completions` endpoint.

#### Examples:

**Ollama** (free, local):
```bash
ollama pull llama3.2
```

**Groq** (free tier):
```json
{ "ai_provider": "groq", "openai_api_key": "gsk_..." }
```

**Any custom API**:
```json
{
  "ai_provider": "openai",
  "openai_base_url": "https://your-api.com/v1",
  "openai_model": "your-model",
  "openai_api_key": "your-key"
}
```
