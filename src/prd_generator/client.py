"""Thin Anthropic client wrapper. Centralizes model + max_tokens config and
the JSON-extraction logic every agent uses."""

from __future__ import annotations

import json
import os
import re
from typing import Any

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

DEFAULT_MODEL = os.getenv("PRD_MODEL", "claude-sonnet-4-6")
DEFAULT_MAX_TOKENS = int(os.getenv("PRD_MAX_TOKENS", "4096"))


def _client() -> Anthropic:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError(
            "ANTHROPIC_API_KEY is not set. Copy .env.example to .env and add a key."
        )
    return Anthropic(api_key=api_key)


def call_agent(
    system: str,
    user: str,
    *,
    model: str | None = None,
    max_tokens: int | None = None,
) -> str:
    """Run a single agent turn and return raw text content."""
    msg = _client().messages.create(
        model=model or DEFAULT_MODEL,
        max_tokens=max_tokens or DEFAULT_MAX_TOKENS,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    parts = [block.text for block in msg.content if getattr(block, "type", "") == "text"]
    return "".join(parts).strip()


_FENCE_RE = re.compile(r"```(?:json)?\s*(.*?)```", re.DOTALL)


def extract_json(text: str) -> Any:
    """Pull the first JSON object/array out of a model response.

    Models love to wrap JSON in ``` fences or prefix it with prose. We strip
    both and parse — raising a clear error if nothing valid is found.
    """
    fenced = _FENCE_RE.search(text)
    if fenced:
        candidate = fenced.group(1).strip()
    else:
        # Find first { or [ and parse from there.
        start = min(
            (i for i in (text.find("{"), text.find("[")) if i >= 0),
            default=-1,
        )
        if start < 0:
            raise ValueError(f"No JSON found in response:\n{text[:400]}")
        candidate = text[start:]
    try:
        return json.loads(candidate)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse JSON: {e}\n\n--- raw ---\n{candidate[:600]}") from e
