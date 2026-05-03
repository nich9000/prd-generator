"""Pydantic models for the PRD output. Each agent in the pipeline returns one
of these and the orchestrator stitches them into the final document.

The schema is deliberately strict so we can fail fast when the model produces
malformed output, and so reviewers can lint a generated PRD against it.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class UserStory(BaseModel):
    """A single user story in the standard role/goal/benefit form."""

    role: str = Field(..., description="Persona, e.g. 'returning shopper'")
    goal: str = Field(..., description="What the user wants to do")
    benefit: str = Field(..., description="Why it matters to them")
    priority: Literal["P0", "P1", "P2"] = "P1"

    def render(self) -> str:
        return f"As a **{self.role}**, I want to {self.goal} so that {self.benefit}."


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
    trigger: str | None = None  # e.g. "the user submits the cart"
    state: str | None = None  # e.g. "the user is signed in"
    unwanted: str | None = None  # e.g. "payment authorization fails"
    feature: str | None = None  # e.g. "Apple Pay is available"
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
    out_of_scope: list[str] = Field(default_factory=list)
    open_questions: list[str] = Field(default_factory=list)

    def to_markdown(self) -> str:
        """Render the PRD as a polished markdown document."""
        lines: list[str] = []
        lines.append(f"# {self.title}\n")
        lines.append(f"> {self.one_liner}\n")
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
        for r in self.risks:
            lines.append(f"- **{r.severity.upper()}** — {r.description}  \n  *Mitigation:* {r.mitigation}")
        if self.out_of_scope:
            lines.append("\n## Out of scope\n")
            for x in self.out_of_scope:
                lines.append(f"- {x}")
        if self.open_questions:
            lines.append("\n## Open questions\n")
            for q in self.open_questions:
                lines.append(f"- {q}")
        return "\n".join(lines).strip() + "\n"
