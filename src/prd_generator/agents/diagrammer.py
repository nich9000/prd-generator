"""Diagrammer agent: produces user-flow + system-context Mermaid diagrams."""

from __future__ import annotations

import json

from ..client import call_agent, extract_json
from ..prompts.system import DIAGRAMMER


def diagram(framing: dict, stories: list[dict]) -> list[dict]:
    user = (
        "Framing:\n"
        + json.dumps(framing, indent=2)
        + "\n\nStories:\n"
        + json.dumps({"stories": stories}, indent=2)
    )
    raw = call_agent(DIAGRAMMER, user)
    data = extract_json(raw)
    diagrams = data.get("diagrams") if isinstance(data, dict) else None
    if not diagrams:
        # Diagrams are nice-to-have, not required. If the model fails, we
        # return an empty list rather than blowing up the whole PRD.
        return []
    return diagrams
