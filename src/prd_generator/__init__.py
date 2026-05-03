"""prd-generator — turn a one-line idea into a PM-grade PRD."""

from .pipeline import generate_prd
from .schema import PRD, UserStory, AcceptanceCriterion, EarsSpec, Risk

__all__ = [
    "generate_prd",
    "PRD",
    "UserStory",
    "AcceptanceCriterion",
    "EarsSpec",
    "Risk",
]

__version__ = "0.1.0"
