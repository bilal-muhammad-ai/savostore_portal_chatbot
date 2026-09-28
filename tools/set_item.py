"""Record item name, info, and quantity for the order draft."""

from langchain_core.tools import tool


@tool
def set_item_name(name: str) -> str:
    """Record the item name. Call only when the user clearly provides a product name."""
    cleaned = name.strip()
    if not cleaned:
        return "Invalid item name. Provide a non-empty name."
    return f"Item name set to {cleaned}."


@tool
def set_item_info(info: str) -> str:
    """Record brief item info or notes. Call when the user provides description/details."""
    cleaned = info.strip()
    if not cleaned:
        return "Invalid item info. Provide a non-empty description."
    return f"Item info set to {cleaned}."


@tool
def set_item_quantity(quantity: int) -> str:
    """Record item quantity. Call only with a positive integer."""
    if quantity < 1:
        return f"Invalid quantity '{quantity}'. Must be a positive integer."
    return f"Item quantity set to {quantity}."
