import asyncio
import json
from datetime import datetime

from rich.syntax import Syntax
from textual import work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal
from textual.widgets import Header, Input, RichLog, Static, Button

from shellchat import ai, config as cfg, shell


CONFIG = cfg.load()
_history_entries: list[dict] = cfg.load_history()


class MessageBubble(Static):
    def __init__(self, text: str, role: str, timestamp: str = "") -> None:
        super().__init__()
        self._text = text
        self._role = role
        self._timestamp = timestamp
        self._source = ""

    def set_source(self, source: str) -> None:
        self._source = source

    def on_mount(self) -> None:
        prefix = "[bold blue]🧑 You[/]" if self._role == "user" else "[bold green]🤖 ShellChat[/]"
        if self._source:
            source_tag = f" [dim white on #333] {self._source} [/]"
        else:
            source_tag = ""
        time_str = f" [dim]{self._timestamp}[/]" if self._timestamp else ""
        self.update(f"{prefix}{source_tag}{time_str}\n{self._text}")


class ChatHistory(RichLog):
    def on_mount(self) -> None:
        self._restore()

    def _restore(self) -> None:
        if not _history_entries:
            self.write("[bold magenta]🐚 Welcome to ShellChat![/]")
            self.write("Type what you want to do in natural language.\n")
            self.write("[dim]📝 Tips: Type naturally → AI suggests a command[/]")
            self.write("[dim]  Type [bold]$[/]command to run raw shell[/]")
            self.write("[dim]  Type [bold]:[/]settings to configure AI[/]")
            self.write("[dim]  Ctrl+L to clear, Esc to cancel[/]\n")
            return
        self.write("[dim]── Restored previous session ──[/]")
        for entry in _history_entries:
            role = entry.get("role", "user")
            text = entry.get("text", "")
            ts = entry.get("timestamp", "")
            source = entry.get("source", "")
            bubble = MessageBubble(text, role, ts)
            if source:
                bubble.set_source(source)
            self.write(bubble)


class CommandInput(Input):
    BINDINGS = [
        Binding("up", "history_up", "History Up", show=False),
        Binding("down", "history_down", "History Down", show=False),
    ]

    def __init__(self) -> None:
        super().__init__(placeholder="Describe what you want to do...")
        self._history: list[str] = []
        self._history_index = -1

    def add_to_history(self, text: str) -> None:
        if text and (not self._history or self._history[-1] != text):
            self._history.append(text)
        self._history_index = len(self._history)

    def action_history_up(self) -> None:
        if self._history and self._history_index > 0:
            self._history_index -= 1
            self.value = self._history[self._history_index]
            self.cursor_position = len(self.value)

    def action_history_down(self) -> None:
        if self._history_index < len(self._history) - 1:
            self._history_index += 1
            self.value = self._history[self._history_index]
            self.cursor_position = len(self.value)
        else:
            self._history_index = len(self._history)
            self.value = ""


class ShellChatApp(App):
    TITLE = "ShellChat"
    SUB_TITLE = "AI-powered chat terminal"

    CSS = """
    Screen {
        background: $surface;
    }
    #chat-container {
        height: 1fr;
        min-height: 10;
        border: none;
    }
    ChatHistory {
        height: 100%;
        border: none;
        background: $surface;
        padding: 0 1;
    }
    #input-container {
        height: auto;
        padding: 0 1 1 1;
        background: $surface;
        border-top: solid $primary;
    }
    CommandInput {
        width: 1fr;
        dock: bottom;
    }
    #button-row {
        height: auto;
        padding: 0 1 1 1;
        background: $surface;
    }
    Button {
        margin: 0 1;
        min-width: 12;
    }
    MessageBubble {
        margin: 0 0 1 0;
        padding: 1;
        background: $boost;
        border: none;
    }
    """

    BINDINGS = [
        Binding("ctrl+l", "clear_chat", "Clear"),
        Binding("ctrl+c", "cancel", "Cancel"),
        Binding("escape", "cancel", "Cancel"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(ChatHistory(id="chat-history"), id="chat-container")
        yield Horizontal(
            Button("Clear", id="clear-btn", variant="error"),
            Button("Help", id="help-btn", variant="default"),
            Button("Settings", id="settings-btn", variant="primary"),
            id="button-row",
        )
        yield CommandInput(id="command-input")

    def on_mount(self) -> None:
        self.query_one(CommandInput).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "clear-btn":
            self.action_clear_chat()
        elif event.button.id == "help-btn":
            self._show_help()
        elif event.button.id == "settings-btn":
            self._show_settings()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        text = event.value.strip()
        if not text:
            return

        cmd_input = self.query_one(CommandInput)
        cmd_input.add_to_history(text)
        cmd_input.clear()

        history = self.query_one(ChatHistory)
        now = datetime.now().strftime("%H:%M")
        history.write(MessageBubble(text, "user", now))

        _history_entries.append({"role": "user", "text": text, "timestamp": now})
        cfg.save_history(_history_entries)

        self._process_input(text)

    def _process_input(self, text: str) -> None:
        if text.startswith(":"):
            self._handle_slash_command(text)
        elif text.startswith("$"):
            self._execute_raw(text[1:].strip(), "shell")
        else:
            self._ask_ai(text)

    def _handle_slash_command(self, text: str) -> None:
        history = self.query_one(ChatHistory)
        now = datetime.now().strftime("%H:%M")
        cmd = text[1:].strip().lower()

        if cmd == "clear":
            self.action_clear_chat()
        elif cmd in ("exit", "quit"):
            history.write(MessageBubble("[yellow]Goodbye![/]", "system", now))
            self.set_timer(0.5, self.exit)
        elif cmd == "help":
            self._show_help()
        elif cmd == "settings":
            self._show_settings()
        elif cmd.startswith("model "):
            CONFIG["model"] = cmd[6:].strip()
            cfg.save(CONFIG)
            history.write(MessageBubble(f"[green]Model set to: {CONFIG['model']}[/]", "system", now))
        elif cmd.startswith("provider "):
            CONFIG["ai_provider"] = cmd[9:].strip()
            cfg.save(CONFIG)
            history.write(MessageBubble(f"[green]Provider set to: {CONFIG['ai_provider']}[/]", "system", now))
        else:
            history.write(MessageBubble(f"[red]Unknown command: :{cmd}[/]", "system", now))

    def _show_help(self) -> None:
        history = self.query_one(ChatHistory)
        history.write("")
        history.write("[bold underline]ShellChat Help[/]")
        history.write("")
        history.write("[bold]🤖 AI Mode (default)[/]")
        history.write("  Type naturally and AI will suggest a command")
        history.write("")
        history.write("[bold]$ Raw Shell[/]")
        history.write("  Prefix with $ to run a command directly")
        history.write("  Example: [bold]$ls -la[/]")
        history.write("")
        history.write("[bold]:commands[/]")
        history.write("  :clear    - Clear chat")
        history.write("  :help     - This help")
        history.write("  :settings - Show current config")
        history.write("  :model <name> - Set AI model")
        history.write("  :provider <ollama|openai> - Set AI provider")
        history.write("  :exit     - Quit")
        history.write("")
        history.write("[bold]Settings file:[/] ~/.shellchat/config.json")
        history.write("")

    def _show_settings(self) -> None:
        history = self.query_one(ChatHistory)
        history.write("")
        history.write("[bold underline]Current Settings[/]")
        for k, v in CONFIG.items():
            if k == "openai_api_key":
                v = f"{'*' * 8}{v[-4:]}" if v else "(not set)"
            history.write(f"  [dim]{k}:[/] {v}")
        history.write("")

    def action_clear_chat(self) -> None:
        history = self.query_one(ChatHistory)
        history.clear()
        _history_entries.clear()
        cfg.save_history(_history_entries)
        history.write("[bold magenta]🐚 Welcome to ShellChat![/]")
        history.write("Type what you want to do in natural language.\n")

    def action_cancel(self) -> None:
        history = self.query_one(ChatHistory)
        history.write("[dim yellow]⏹ Cancelled.[/]\n")

    @work(exclusive=True)
    async def _ask_ai(self, text: str) -> None:
        history = self.query_one(ChatHistory)
        now = datetime.now().strftime("%H:%M")

        ai_messages = []
        for entry in _history_entries[-10:]:
            if entry["role"] in ("user", "assistant"):
                ai_messages.append({"role": entry["role"], "content": entry["text"]})
        ai_messages.append({"role": "user", "content": text})

        history.write(MessageBubble("[dim]🤔 Thinking...[/]", "system", now))

        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, ai.ask, CONFIG, ai_messages)

        command = result.get("command", "")
        explanation = result.get("explanation", "")
        safe = result.get("safe", True)

        if not command:
            history.write(MessageBubble(f"🧠 {explanation}", "assistant", now))
            _history_entries.append({"role": "assistant", "text": explanation, "timestamp": now, "source": "ai"})
            cfg.save_history(_history_entries)
            return

        response = f"🧠 [bold]{explanation}[/]\n\n[dim]└─ Will run:[/] [bold yellow]{command}[/]"
        if not safe:
            response += "\n\n[bold red]⚠ Unsafe command — type [bold]:confirm[/] to execute or press Esc to cancel[/]"
        history.write(MessageBubble(response, "assistant", now))

        _history_entries.append({"role": "assistant", "text": f"{explanation}\n$ {command}", "timestamp": now, "source": "ai"})
        cfg.save_history(_history_entries)

        if safe or CONFIG.get("auto_execute", True):
            self._execute_raw(command, "exec")
        else:
            self._pending_command = command

    def _execute_raw(self, command: str, source: str) -> None:
        if not command:
            return
        history = self.query_one(ChatHistory)
        now = datetime.now().strftime("%H:%M")
        self.run_worker(self._stream_command(command, history, now, source))

    async def _stream_command(self, command: str, history, now: str, source: str) -> None:
        running_bubble = MessageBubble(f"[dim]⏳ Running:[/] [bold yellow]{command}[/]", "system", now)
        self.call_from_thread(history.write, running_bubble)

        lines = await shell.run_command(command, CONFIG.get("timeout", 60))

        if not lines:
            self.call_from_thread(
                history.write,
                MessageBubble("[dim]Command completed with no output.[/]", "system", now),
            )
            return

        stdout_lines = [line for stream, line in lines if stream == "stdout"]
        stderr_lines = [line for stream, line in lines if stream == "stderr"]

        parts = []
        if stdout_lines:
            text = "\n".join(stdout_lines)
            try:
                syntax = Syntax(text, "bash", theme="monokai", word_wrap=True)
                parts.append(str(syntax))
            except Exception:
                parts.append(text)

        if stderr_lines:
            parts.append(f"[dim red]{chr(10).join(stderr_lines)}[/]")

        output = "\n\n".join(parts) if parts else "[dim]Command completed with no output.[/]"
        result_bubble = MessageBubble(output, "system", now)
        self.call_from_thread(history.write, result_bubble)

        _history_entries.append({"role": "assistant", "text": f"$ {command}\n{output}", "timestamp": now, "source": source})
        cfg.save_history(_history_entries)
