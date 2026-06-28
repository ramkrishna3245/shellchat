import asyncio
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from textual import work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.reactive import reactive
from textual.widgets import Header, Footer, Input, RichLog, Static, Button


class MessageBubble(Static):
    def __init__(self, text: str, role: str, timestamp: str = "") -> None:
        super().__init__()
        self._text = text
        self._role = role
        self._timestamp = timestamp

    def on_mount(self) -> None:
        prefix = "[bold blue]🧑 You[/]" if self._role == "user" else "[bold green]🤖 ShellChat[/]"
        time_str = f" [dim]{self._timestamp}[/]" if self._timestamp else ""
        content = self._text.replace("[", "[[")
        content = content.replace("]", "]]")
        self.update(f"{prefix}{time_str}\n{content}")


class ChatHistory(RichLog):
    def on_mount(self) -> None:
        self.write("[bold magenta]🐚 Welcome to ShellChat![/]")
        self.write("Type a message or command below to start chatting.\n")
        self.write("[dim]Tips: Use Ctrl+C to cancel, Ctrl+L to clear[/]\n")


class CommandInput(Input):
    BINDINGS = [
        Binding("up", "history_up", "History Up", show=False),
        Binding("down", "history_down", "History Down", show=False),
    ]

    def __init__(self) -> None:
        super().__init__(placeholder="Type a message or command...")
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
    SUB_TITLE = "Chat-style terminal"

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
        yield Container(
            ChatHistory(id="chat-history"),
            id="chat-container",
        )
        yield Horizontal(
            Button("Clear", id="clear-btn", variant="error"),
            Button("Help", id="help-btn", variant="default"),
            id="button-row",
        )
        yield CommandInput(id="command-input")

    def on_mount(self) -> None:
        self.query_one(CommandInput).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "clear-btn":
            self.action_clear_chat()
        elif event.button.id == "help-btn":
            self.show_help()

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

        self.handle_message(text)

    def show_help(self) -> None:
        history = self.query_one(ChatHistory)
        history.write("")
        history.write("[bold underline]ShellChat Help[/]")
        history.write("Type a message or command and press Enter.")
        history.write("Commands are executed in your system shell.")
        history.write("")
        history.write("[bold]Special commands:[/]")
        history.write("  [italic]:clear[/]  - Clear chat history")
        history.write("  [italic]:help[/]   - Show this help")
        history.write("  [italic]:exit[/]   - Exit ShellChat")
        history.write("")
        history.write("[bold]Tips:[/]")
        history.write("  Ctrl+L  - Clear chat")
        history.write("  Up/Down - Command history")
        history.write("  Esc     - Cancel running command")
        history.write("")

    def action_clear_chat(self) -> None:
        history = self.query_one(ChatHistory)
        history.clear()
        history.write("[bold magenta]🐚 Welcome to ShellChat![/]")
        history.write("Type a message or command below to start chatting.\n")

    def action_cancel(self) -> None:
        history = self.query_one(ChatHistory)
        history.write("[dim yellow]⏹ Cancelled.[/]\n")

    @work(exclusive=True, thread=True)
    async def handle_message(self, text: str) -> None:
        history = self.query_one(ChatHistory)
        now = datetime.now().strftime("%H:%M")

        if text.startswith(":"):
            self.handle_special_command(text)
            return

        try:
            result = subprocess.run(
                text,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30,
            )

            output_parts = []
            if result.stdout:
                output_parts.append(result.stdout.rstrip())
            if result.stderr:
                output_parts.append(f"[dim red]{result.stderr.rstrip()}[/]")

            if output_parts:
                output_text = "\n".join(output_parts)
            else:
                output_text = "[dim]Command completed with no output.[/]"

            exit_code = result.returncode
            status = "✅" if exit_code == 0 else "❌"
            response = f"{output_text}\n\n[dim]{status} Exit code: {exit_code}[/]"

        except subprocess.TimeoutExpired:
            response = "[red]⏱ Command timed out after 30 seconds.[/]"
        except Exception as e:
            response = f"[red]⚠ Error: {e}[/]"

        self.call_from_thread(history.write, MessageBubble(response, "system", now))

    def handle_special_command(self, text: str) -> None:
        history = self.query_one(ChatHistory)
        now = datetime.now().strftime("%H:%M")

        cmd = text[1:].strip().lower()
        if cmd == "clear":
            self.action_clear_chat()
        elif cmd in ("exit", "quit"):
            history.write(MessageBubble("[yellow]Goodbye![/]", "system", now))
            self.set_timer(0.5, self.exit)
        elif cmd == "help":
            self.show_help()
        else:
            history.write(MessageBubble(f"[red]Unknown command: :{cmd}[/]", "system", now))
