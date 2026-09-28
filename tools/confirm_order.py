"""Confirm or decline the completed order draft."""

from langchain_core.tools import tool


@tool
def confirm_order(confirmed: bool) -> str:
    """Record final order confirmation. Call only when the user clearly confirms or declines."""
    if confirmed:
        return "Order confirmed."
    return "Order confirmation declined. Ask the user to review and confirm again."
