"""Record whether the user accepted the shipping agreement."""

from langchain_core.tools import tool


@tool
def set_agreement(accepted: bool) -> str:
    """Record agreement acceptance. Call only when the user clearly agrees or declines."""
    if accepted:
        return "Agreement accepted."
    return "Agreement declined. User must accept the shipping note to continue."
