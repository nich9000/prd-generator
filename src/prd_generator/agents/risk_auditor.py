"""Risk auditor agent: produces risks, out-of-scope, and open questions."""

from __future__ import annotations

import json

from ..client import call_agent, extract_json
from ..prompts.system import RISK_AUDITOR


def audit_risks(framing: dict, stories: list[dict]) -> dict:
    user = "Framing:\n" + json.dumps(framing, indent=2) + "\n\nStories:\n" + json.dumps(
        {"stories": stories}, indent=2
    )
    raw = call_agent(RISK_AUDITOR, user)
    data = extract_json(raw)
    if not isinstance(data, dict) or "risks" not in data:
        raise ValueError(f"Risk auditor returned malformed output.\nRaw: {raw[:400]}")
    data.setdefault("out_of_scope", [])
    data.setdefault("open_questions", [])
    return data
