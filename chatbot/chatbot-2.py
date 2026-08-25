#!/usr/bin/env python3
"""Modern text UI chatbot that talks to an OpenAI-compatible chat completions API.

Configuration (environment variables):
  SOCLAAS_API_KEY   - API key sent as a Bearer token
  SOCLAAS_BASE_URL  - versioned API root URL, e.g. https://api.example.com/v1
  SOCLAAS_MODEL     - model name to request

The endpoint is formed by appending /chat/completions to SOCLAAS_BASE_URL.

UI dependencies (pip install rich prompt_toolkit):
  - rich: styled output, Markdown rendering, panels
  - prompt_toolkit: line editing, history, and a help toolbar in the input box

Built-in commands (typed at the prompt):
  /clear   - clear the conversation history
  /quit    - exit the chatbot (Ctrl-D or Ctrl-C also work)
"""

import json
import os
import sys
import urllib.error
import urllib.request

from prompt_toolkit import PromptSession
from prompt_toolkit.formatted_text import ANSI
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.styles import Style
from rich.console import Console, Group
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text


def load_config():
    """Read and validate configuration from environment variables."""
    api_key = os.environ.get("SOCLAAS_API_KEY")
    base_url = os.environ.get("SOCLAAS_BASE_URL")
    model = os.environ.get("SOCLAAS_MODEL")

    missing = [
        name
        for name, value in (
            ("SOCLAAS_API_KEY", api_key),
            ("SOCLAAS_BASE_URL", base_url),
            ("SOCLAAS_MODEL", model),
        )
        if not value
    ]
    if missing:
        sys.exit(
            "error: missing required environment variable(s): "
            + ", ".join(missing)
        )

    # Endpoint is the versioned base URL plus the chat completions path.
    endpoint = base_url.rstrip("/") + "/chat/completions"
    return api_key, endpoint, model


def ask_llm(endpoint, api_key, model, messages):
    """Send `messages` to the chat completions endpoint and return the reply."""
    payload = json.dumps({"model": model, "messages": messages}).encode("utf-8")
    request = urllib.request.Request(
        endpoint,
        data=payload,
        method="POST",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(request, timeout=120) as response:
        body = json.loads(response.read().decode("utf-8"))

    try:
        return body["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise ValueError(f"unexpected API response: {json.dumps(body)[:500]}") from exc


class ChatUI:
    """Terminal UI: renders the conversation and reads user input."""

    def __init__(self, model):
        self.console = Console()
        self.model = model
        self.session = PromptSession(history=InMemoryHistory())

    def banner(self):
        title = Text("Chatbot", style="bold cyan")
        subtitle = Text(
            f"model: {self.model}  |  /clear resets history, /quit exits",
            style="dim",
        )
        self.console.print(
            Panel(Group(title, subtitle), border_style="cyan", expand=False)
        )

    def show_user(self, message):
        self.console.print(
            Group(
                Text("You", style="bold green"),
                Text(message, style="green"),
                Text("", style="dim"),
            )
        )

    def thinking(self):
        spinner = Live(
            Text("Thinking…", style="italic dim cyan"),
            console=self.console,
            auto_refresh=True,
        )
        spinner.start()
        return spinner

    def show_assistant(self, reply):
        self.console.print(Text("Assistant", style="bold magenta"))
        self.console.print(
            Panel(Markdown(reply), border_style="magenta", expand=False)
        )
        self.console.print()

    def show_error(self, message):
        self.console.print(f"[bold red]error:[/bold red] {message}")
        self.console.print()

    def read_input(self):
        """Read one line of user input, or None on Ctrl-D / Ctrl-C."""
        try:
            return self.session.prompt(
                "> ",
                style=Style.from_dict({"prompt": "bold cyan"}),
                bottom_toolbar=lambda: ANSI(
                    "\x1b[2mCtrl-D exit  ·  /clear  ·  /quit\x1b[0m"
                ),
            )
        except (EOFError, KeyboardInterrupt):
            return None


def main():
    api_key, endpoint, model = load_config()

    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant.",
        }
    ]

    ui = ChatUI(model)
    ui.banner()

    while True:
        user_input = ui.read_input()
        if user_input is None:
            ui.console.print("\n[dim]Bye![/dim]")
            break

        user_input = user_input.strip()
        if not user_input:
            continue

        if user_input in ("/quit", "/exit", "/q"):
            ui.console.print("[dim]Bye![/dim]")
            break

        if user_input in ("/clear", "/reset"):
            messages = [
                {
                    "role": "system",
                    "content": "You are a helpful assistant.",
                }
            ]
            ui.console.print("[dim]Conversation history cleared.[/dim]\n")
            continue

        ui.show_user(user_input)
        messages.append({"role": "user", "content": user_input})

        with ui.thinking() as spinner:
            try:
                reply = ask_llm(endpoint, api_key, model, messages)
            except urllib.error.HTTPError as exc:
                detail = exc.read().decode("utf-8", "replace")[:500]
                spinner.stop()
                ui.show_error(f"HTTP {exc.code} {exc.reason}: {detail}")
                # Drop the unanswered user turn so the next message starts fresh.
                messages.pop()
                continue
            except (urllib.error.URLError, ValueError, OSError) as exc:
                spinner.stop()
                ui.show_error(str(exc))
                messages.pop()
                continue

        ui.show_assistant(reply)
        messages.append({"role": "assistant", "content": reply})


if __name__ == "__main__":
    main()
