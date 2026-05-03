"""Schema rendering tests. These run without an API key."""

from prd_generator.schema import (
    AcceptanceCriterion,
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


def test_prd_to_markdown_includes_all_sections():
    prd = PRD(
        title="Saved Cart Recovery",
        one_liner="Recover abandoned carts on next app open.",
        problem="Users lose carts when they switch contexts.",
        target_user="Returning mobile shoppers",
        success_metrics=["Reduce abandonment by 10pts"],
        user_stories=[
            UserStory(role="shopper", goal="restore my cart", benefit="I save time")
        ],
        acceptance_criteria=[
            AcceptanceCriterion(given="cart exists", when="I open app", then="banner shows")
        ],
        ears_specs=[
            EarsSpec(
                pattern="ubiquitous",
                system="recovery service",
                behavior="log every banner event",
            )
        ],
        risks=[Risk(description="Stale flagging wrong", severity="high", mitigation="Beta gate")],
    )
    md = prd.to_markdown()
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
