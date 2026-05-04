"""Schema rendering tests. These run without an API key."""

from prd_generator.schema import (
    AcceptanceCriterion,
    Diagram,
    EarsSpec,
    PRD,
    Risk,
    UserStory,
)


def test_user_story_renders_in_role_goal_benefit_form():
    s = UserStory(role="shopper", goal="restore my cart", benefit="I don't lose items")
    assert s.render() == (
        "As a **shopper**, I want to restore my cart so that I don't lose items."
    )


def test_user_story_strips_duplicated_prefixes():
    """If the model leaks 'As an' / 'I want to' / 'so that' into the values,
    the renderer must NOT double them up."""
    s = UserStory(
        role="As an iOS shopper",
        goal="I want to pay with Apple Pay",
        benefit="so that I can check out faster",
    )
    assert s.render() == (
        "As a **iOS shopper**, I want to pay with Apple Pay so that I can check out faster."
    )


def test_acceptance_criterion_uses_given_when_then():
    ac = AcceptanceCriterion(given="I have an abandoned cart", when="I open the app", then="a banner appears")
    out = ac.render()
    assert "**Given**" in out and "**When**" in out and "**Then**" in out


def test_ears_event_pattern_renders_correctly():
    spec = EarsSpec(
        pattern="event",
        trigger="the user opens the app",
        system="cart-recovery service",
        behavior="render the recovery banner",
    )
    assert spec.render() == (
        "When the user opens the app, the cart-recovery service shall render the recovery banner."
    )


def test_ears_unwanted_pattern_uses_if_then():
    spec = EarsSpec(
        pattern="unwanted",
        unwanted="cart-sync fails",
        system="recovery banner",
        behavior="be suppressed",
    )
    assert spec.render() == (
        "If cart-sync fails, then the recovery banner shall be suppressed."
    )


def test_diagram_strips_accidental_fences():
    """The model sometimes wraps Mermaid in ``` fences; our render() must
    strip them so we don't get nested fences."""
    d = Diagram(
        title="User flow",
        kind="user_flow",
        mermaid="```mermaid\nflowchart TD\n    A[Start] --> B[End]\n```",
    )
    rendered = d.render()
    assert rendered.startswith("### User flow\n\n```mermaid\n")
    assert rendered.count("```mermaid") == 1
    # No double-fenced or stray ``` left in the body
    body = rendered.split("```mermaid", 1)[1]
    assert body.count("```") == 1


def test_diagram_renders_clean_mermaid_block():
    d = Diagram(
        title="System context",
        kind="system_context",
        mermaid="flowchart LR\n    A --> B",
    )
    expected = "### System context\n\n```mermaid\nflowchart LR\n    A --> B\n```"
    assert d.render() == expected


def _make_prd(**overrides):
    base = dict(
        title="Saved Cart Recovery",
        one_liner="Recover abandoned carts on next app open.",
        problem="Users lose carts when they switch contexts.",
        target_user="Returning mobile shoppers",
        success_metrics=["Reduce abandonment by 10pts"],
        user_stories=[
            UserStory(role="shopper", goal="restore my cart", benefit="I save time", priority="P0")
        ],
        acceptance_criteria=[
            AcceptanceCriterion(given="cart exists", when="I open app", then="banner shows")
        ],
        ears_specs=[
            EarsSpec(pattern="ubiquitous", system="recovery service", behavior="log every banner event")
        ],
        risks=[Risk(description="Stale flagging wrong", severity="high", mitigation="Beta gate")],
    )
    base.update(overrides)
    return PRD(**base)


def test_prd_to_markdown_includes_all_sections():
    md = _make_prd().to_markdown()
    for header in (
        "# Saved Cart Recovery",
        "## Problem",
        "## Target user",
        "## Success metrics",
        "## User stories",
        "## Acceptance criteria",
        "## Requirements (EARS)",
        "## Risks",
    ):
        assert header in md


def test_prd_at_a_glance_table_renders_at_top():
    md = _make_prd().to_markdown()
    # Table must appear before the Problem section
    table_idx = md.find("| **Primary metric** |")
    problem_idx = md.find("## Problem")
    assert table_idx > 0 and problem_idx > 0
    assert table_idx < problem_idx
    assert "| **Top risk** |" in md
    assert "| **Scope** |" in md


def test_prd_risks_render_as_github_alerts():
    """High severity should map to !CAUTION, medium to !WARNING, low to !NOTE."""
    md = _make_prd(
        risks=[
            Risk(description="Critical thing", severity="high", mitigation="Beta"),
            Risk(description="Mid thing", severity="medium", mitigation="A/B"),
            Risk(description="Minor thing", severity="low", mitigation="Monitor"),
        ]
    ).to_markdown()
    assert "> [!CAUTION]" in md
    assert "> [!WARNING]" in md
    assert "> [!NOTE]" in md
    # And the high-severity risk should be ordered first
    assert md.find("> [!CAUTION]") < md.find("> [!WARNING]") < md.find("> [!NOTE]")


def test_prd_diagrams_render_in_overview_section():
    prd = _make_prd(
        diagrams=[
            Diagram(title="User flow", kind="user_flow", mermaid="flowchart TD\n    A --> B"),
            Diagram(title="System context", kind="system_context", mermaid="flowchart LR\n    X --> Y"),
        ]
    )
    md = prd.to_markdown()
    assert "## Overview" in md
    assert "### User flow" in md and "### System context" in md
    assert md.find("## Overview") < md.find("## Problem")


def test_prd_with_no_diagrams_skips_overview_section():
    md = _make_prd().to_markdown()
    assert "## Overview" not in md
