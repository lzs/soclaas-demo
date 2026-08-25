#!/usr/bin/env python3
"""Simple chatbot that talks to an OpenAI-compatible chat completions API.

Configuration (environment variables):
  SOCLAAS_API_KEY   - API key sent as a Bearer token
  SOCLAAS_BASE_URL  - versioned API root URL, e.g. https://api.example.com/v1
  SOCLAAS_MODEL     - model name to request

The endpoint is formed by appending /chat/completions to SOCLAAS_BASE_URL.
Uses only the Python standard library.
"""

import json
import os
import sys
import urllib.error
import urllib.request


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


def main():
    api_key, endpoint, model = load_config()

    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant.",
        }
    ]

    print("Chatbot ready. Type a message and press Enter (Ctrl-D to quit).")

    while True:
        try:
            user_input = input("> ")
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not user_input.strip():
            continue

        messages.append({"role": "user", "content": user_input})
        try:
            reply = ask_llm(endpoint, api_key, model, messages)
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", "replace")[:500]
            print(f"error: HTTP {exc.code} {exc.reason}: {detail}", file=sys.stderr)
            # Drop the unanswered user turn so the next message starts fresh.
            messages.pop()
            continue
        except (urllib.error.URLError, ValueError, OSError) as exc:
            print(f"error: {exc}", file=sys.stderr)
            messages.pop()
            continue

        print(reply)
        messages.append({"role": "assistant", "content": reply})


if __name__ == "__main__":
    main()
