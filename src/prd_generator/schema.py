"""Pydantic models for the PRD output. Each agent in the pipeline returns one
of these and the orchestrator stitches them into the final document.

The schema is deliberately strict so we can fail fast when the model produces
malformed output, and so reviewers can lint a generated PRD against it.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


def _strip_prefix(text: str, prefixes: tuple[str, ...]) -> str:
    """Remove any leading prefix (case-insensitive) so we don't double-wrap
    when a model returns 'As an X' instead of just 'X'."""
    stripped = text.lstrip()
    lower = stripped.lower()
    for p in prefixes:
        if lower.startswith(p.lower()):
            return stripped[len(p):].lstrip()
    return stripped


class UserStory(BaseModel):
    """A single user story in the standard role/goal/benefit form."""

    role: str = Field(..., description="Persona, e.g. 'returning shopper'")
    goal: str = Field(..., description="What the user wants to do")
    benefit: str = Field(..., description="Why it matters to them")
    priority: Literal["P0", "P1", "P2"] = "P1"

    def render(self) -> str:
        role = _strip_prefix(self.role, ("As an ", "As a "))
        goal = _strip_prefix(self.goal, ("I want to ", "I want ", "I'd like to "))
        benefit = _strip_prefix(self.benefit, ("so that ", "so ", "in order to ", "to "))
        return f"As a **{role}**, I want to {goal} so that {benefit}."


class AcceptanceCriterion(BaseModel):
    """Given/When/Then style acceptance criterion attached to a story."""

    given: str
    when: str
    then: str

    def render(self) -> str:
        return f"- **Given** {self.given}\n- **When** {self.when}\n- **Then** {self.then}"


class EarsSpec(BaseModel):
    """An EARS-template requirement.

    EARS = Easy Approach to Requirements Syntax. Each requirement is one of:
      - Ubiquitous:   "The <system> shall <behavior>."
      - Event-driven: "When <trigger>, the <system> shall <behavior>."
      - State-driven: "While <state>, the <system> shall <behavior>."
      - Unwanted:     "If <unwanted>, then the <system> shall <behavior>."
      - Optional:     "Where <feature>, the <system> shall <behavior>."
    """

    pattern: Literal["ubiquitous", "event", "state", "unwanted", "optional"]
    trigger: str | None = None
    state: str | None = None
    unwanted: str | None = None
    feature: str | None = None
    system: str = Field(..., description="Subject of the requirement")
    behavior: str = Field(..., description="What the system does")

    def render(self) -> str:
        s, b = self.system, self.behavior
        if self.pattern == "ubiquitous":
            return f"The {s} shall {b}."
        if self.pattern == "event":
            return f"When {self.trigger}, the {s} shall {b}."
        if self.pattern == "state":
            return f"While {self.state}, the {s} shall {b}."
        if self.pattern == "unwanted":
            return f"If {self.unwanted}, then the {s} shall {b}."
        if self.pattern == "optional":
            return f"Where {self.feature}, the {s} shall {b}."
        return f"The {s} shall {b}."


class Risk(BaseModel):
    description: str
    severity: Literal["low", "medium", "high"]
    mitigation: str


class Diagram(BaseModel):
    """A Mermaid diagram block. GitHub renders these natively in .md files."""

    title: str = Field(..., description="Short title shown above the diagram")
    kind: Literal["user_flow", "system_context", "state", "sequence", "other"]
    mermaid: str = Field(..., description="Raw Mermaid source, no fences")

    def render(self) -> str:
        # Strip any accidental fences the model might have included.
        code = self.mermaid.strip()
        if code.startswith("```"):
            code = code.split("\n", 1)[1] if "\n" in code else ""
            if code.endswith("```"):
                code = code.rsplit("```", 1)[0]
        code = code.strip()
        return f"### {self.title}\n\n```mermaid\n{code}\n```"


# Map risk severity to GitHub-flavored alert blocks. These render with
# colored borders + icons in the GitHub web view.
_SEVERITY_ALERT = {
    "high": "CAUTION",
    "medium": "WARNING",
    "low": "NOTE",
}


class PRD(BaseModel):
    title: str
    one_liner: str = Field(..., description="The original one-line idea")
    problem: str = Field(..., description="Customer problem in 1-3 sentences")
    target_user: str = Field(..., description="Primary persona")
    success_metrics: list[str] = Field(..., description="3-5 measurable outcomes")
    user_stories: list[UserStory]
    acceptance_criteria: list[AcceptanceCriterion]
    ears_specs: list[EarsSpec]
    risks: list[Risk]
    diagrams: list[Diagram] = Field(default_factory=list)
    out_of_scope: list[str] = Field(default_factory=list)
    open_questions: list[str] = Field(default_factory=list)

    def _at_a_glance_table(self) -> str:
        """A 4-row summary table for fast scanning at the top of the doc."""
        p0_count = sum(1 for s in self.user_stories if s.priority == "P0")
        # Pick the highest-severity risk for the headline.
        order = {"high": 0, "medium": 1, "low": 2}
        sorted_risks = sorted(self.risks, key=lambda r: order.get(r.severity, 3))
        top_risk = sorted_risks[0] if sorted_risks else None
        primary_metric = self.success_metrics[0] if self.success_metrics else "—"

        risk_cell = (
            f"{top_risk.severity.upper()} — {top_risk.description}"
            if top_risk
            else "—"
        )
        return (
            "| | |\n"
            "|---|---|\n"
            f"| **Primary metric** | {primary_metric} |\n"
            f"| **Top risk** | {risk_cell} |\n"
            f"| **Scope** | {len(self.user_stories)} stories ({p0_count} P0) · {len(self.ears_specs)} requirements |\n"
            f"| **Persona** | {self.target_user} |\n"
        )

    def to_markdown(self) -> str:
        """Render the PRD as a polished markdown document."""
        lines: list[str] = []
        lines.append(f"# {self.title}\n")
        lines.append(f"> {self.one_liner}\n")
        lines.append(self._at_a_glance_table())
        if self.diagrams:
            lines.append("\n## Overview\n")
            for d in self.diagrams:
                lines.append(d.render() + "\n")
        lines.append("## Problem\n")
        lines.append(self.problem + "\n")
        lines.append("## Target user\n")
        lines.append(self.target_user + "\n")
        lines.append("## Success metrics\n")
        for m in self.success_metrics:
            lines.append(f"- {m}")
        lines.append("\n## User stories\n")
        for i, s in enumerate(self.user_stories, 1):
            lines.append(f"**US-{i:02d} ({s.priority}).** {s.render()}\n")
        lines.append("## Acceptance criteria\n")
        for i, ac in enumerate(self.acceptance_criteria, 1):
            lines.append(f"**AC-{i:02d}**\n\n{ac.render()}\n")
        lines.append("## Requirements (EARS)\n")
        for i, r in enumerate(self.ears_specs, 1):
            lines.append(f"- **R-{i:02d}** {r.render()}")
        lines.append("\n## Risks\n")
        # Group risks by severity, render each as a GitHub alert block.
        order = {"high": 0, "medium": 1, "low": 2}
        sorted_risks = sorted(self.risks, key=lambda r: order.get(r.severity, 3))
        for r in sorted_risks:
            alert = _SEVERITY_ALERT.get(r.severity, "NOTE")
            lines.append(
                f"> [!{alert}]\n"
                f"> **{r.severity.upper()}** — {r.description}\n"
                f">\n"
                f"> *Mitigation:* {r.mitigation}\n"
            )
        if self.out_of_scope:
            lines.append("## Out of scope\n")
            for x in self.out_of_scope:
                lines.append(f"- {x}")
        if self.open_questions:
            lines.append("\n## Open questions\n")
            for q in self.open_questions:
                lines.append(f"- {q}")
        return "\n".join(lines).strip() + "\n"
