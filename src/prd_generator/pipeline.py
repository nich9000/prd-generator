"""Orchestrator. Runs the five agents in dependency order and assembles a
fully-typed PRD object."""

from __future__ import annotations

from .agents import (
    audit_risks,
    author_ears,
    frame,
    write_acceptance,
    write_stories,
)
from .schema import PRD


def generate_prd(one_liner: str) -> PRD:
    """End-to-end pipeline. Each step depends on the previous step's output."""
    framing = frame(one_liner)
    stories = write_stories(framing)
    acceptance = write_acceptance(stories)
    ears = author_ears(acceptance)
    risk_block = audit_risks(framing, stories)

    return PRD(
        title=framing["title"],
        one_liner=one_liner.strip(),
        problem=framing["problem"],
        target_user=framing["target_user"],
        success_metrics=framing["success_metrics"],
        user_stories=stories,
        acceptance_criteria=acceptance,
        ears_specs=ears,
        risks=risk_block["risks"],
        out_of_scope=risk_block.get("out_of_scope", []),
        open_questions=risk_block.get("open_questions", []),
    )
