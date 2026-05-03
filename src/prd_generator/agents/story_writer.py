"""Story writer agent: produces 4-8 user stories from a PRD framing."""

from __future__ import annotations

import json

from ..client import call_agent, extract_json
from ..prompts.system import STORY_WRITER


def write_stories(framing: dict) -> list[dict]:
    user = "PRD framing:\n" + json.dumps(framing, indent=2)
    raw = call_agent(STORY_WRITER, user)
    data = extract_json(raw)
    stories = data.get("stories") if isinstance(data, dict) else None
    if not stories:
        raise ValueError(f"Story writer returned no stories.\nRaw: {raw[:400]}")
    return stories
