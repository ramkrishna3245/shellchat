# ShellChat 🐚💬

Turn your terminal into a ChatGPT-like chat experience.

No more remembering complex shell commands — just type what you want in natural language, and ShellChat runs it for you in a beautiful chat-style TUI.

## Features

- Chat-style interface in your terminal
- Execute any shell command by typing it naturally
- Syntax-highlighted output
- Command history (Up/Down arrow)
- Session persistence
- Beautiful Textual-based TUI

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python -m shellchat
```

Or after installing:

```bash
shellchat
```

Type a command and press Enter. Your command runs in the system shell and the output appears in a chat bubble.

### Special Commands

| Command  | Action           |
|----------|------------------|
| `:clear` | Clear chat       |
| `:help`  | Show help        |
| `:exit`  | Exit ShellChat   |

### Keyboard Shortcuts

| Key     | Action           |
|---------|------------------|
| Enter   | Send message     |
| Up/Down | Command history  |
| Ctrl+L  | Clear chat       |
| Esc     | Cancel operation |
