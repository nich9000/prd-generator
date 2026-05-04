"""Orchestrator. Runs the agents in dependency order and assembles a
fully-typed PRD object."""

from __future__ import annotations

from .agents import (
    audit_risks,
    author_ears,
    diagram,
    frame,
    write_acceptance,
    write_stories,
)
from .schema import PRD


def generate_prd(one_liner: str, *, with_diagrams: bool = True) -> PRD:
    """End-to-end pipeline. Each step depends on the previous step's output.

    Args:
        one_liner: The product idea in a single sentence.
        with_diagrams: When True (default), runs the diagrammer agent and
            embeds Mermaid diagrams in the PRD. Set False to skip the extra
            API call (saves ~$0.02/run).
    """
    framing = frame(one_liner)
    stories = write_stories(framing)
    acceptance = write_acceptance(stories)
    ears = author_ears(acceptance)
    risk_block = audit_risks(framing, stories)
    diagrams = diagram(framing, stories) if with_diagrams else []

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
        diagrams=diagrams,
        out_of_scope=risk_block.get("out_of_scope", []),
        open_questions=risk_block.get("open_questions", []),
    )
