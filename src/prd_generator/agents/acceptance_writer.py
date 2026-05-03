"""Acceptance criteria agent: turns stories into Given/When/Then."""

from __future__ import annotations

import json

from ..client import call_agent, extract_json
from ..prompts.system import ACCEPTANCE_WRITER


def write_acceptance(stories: list[dict]) -> list[dict]:
    user = "User stories:\n" + json.dumps({"stories": stories}, indent=2)
    raw = call_agent(ACCEPTANCE_WRITER, user)
    data = extract_json(raw)
    acs = data.get("acceptance_criteria") if isinstance(data, dict) else None
    if not acs:
        raise ValueError(f"Acceptance writer returned nothing.\nRaw: {raw[:400]}")
    return acs
