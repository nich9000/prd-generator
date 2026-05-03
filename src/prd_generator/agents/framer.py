"""Framer agent: turn a one-line idea into title/problem/target/metrics."""

from __future__ import annotations

from ..client import call_agent, extract_json
from ..prompts.system import FRAMER


def frame(one_liner: str) -> dict:
    user = f"One-line product idea:\n{one_liner.strip()}"
    raw = call_agent(FRAMER, user)
    data = extract_json(raw)
    required = {"title", "problem", "target_user", "success_metrics"}
    missing = required - set(data)
    if missing:
        raise ValueError(f"Framer agent missing fields: {missing}\nRaw: {raw[:400]}")
    return data
