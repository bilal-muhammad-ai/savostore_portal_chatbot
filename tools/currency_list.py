"""Currency list tool for order creation."""

from langchain_core.tools import tool


@tool
def get_currency_list() -> list[dict]:
    """Return available order currencies (id and name). Call after the user accepts the shipping agreement."""
    return [
        {"id": "KES", "name": "Kenyan Shilling"},
        {"id": "USD", "name": "US Dollar"},
    ]
