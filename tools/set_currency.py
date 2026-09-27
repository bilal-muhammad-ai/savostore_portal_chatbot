"""Record the user's selected order currency."""

from langchain_core.tools import tool

_ALLOWED = {"KES", "USD"}


@tool
def set_currency(currency_id: str) -> str:
    """Record the user's chosen currency id (KES or USD). Call only after they clearly select one."""
    normalized = currency_id.strip().upper()
    if normalized not in _ALLOWED:
        return f"Invalid currency_id '{currency_id}'. Allowed: {', '.join(sorted(_ALLOWED))}."
    return f"Currency set to {normalized}."
