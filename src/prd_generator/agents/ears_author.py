"""EARS author agent: translates acceptance criteria into EARS specs."""

from __future__ import annotations

import json

from ..client import call_agent, extract_json
from ..prompts.system import EARS_AUTHOR


def author_ears(acceptance: list[dict]) -> list[dict]:
    user = "Acceptance criteria:\n" + json.dumps(
        {"acceptance_criteria": acceptance}, indent=2
    )
    raw = call_agent(EARS_AUTHOR, user)
    data = extract_json(raw)
    specs = data.get("ears_specs") if isinstance(data, dict) else None
    if not specs:
        raise ValueError(f"EARS author returned nothing.\nRaw: {raw[:400]}")
    # Normalize null fields the schema expects to be missing.
    for s in specs:
        for k in ("trigger", "state", "unwanted", "feature"):
            if s.get(k) in ("", None):
                s[k] = None
    return specs
