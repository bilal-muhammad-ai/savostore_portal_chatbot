"""Record the user's selected warehouse."""

from langchain_core.tools import tool

from tools.warehouse_list import WAREHOUSES

_ALLOWED = {w["id"] for w in WAREHOUSES}


@tool
def set_warehouse(warehouse_id: str) -> str:
    """Record the user's chosen warehouse id. Call only after they clearly select one."""
    normalized = warehouse_id.strip().upper()
    if normalized not in _ALLOWED:
        return f"Invalid warehouse_id '{warehouse_id}'. Allowed: {', '.join(sorted(_ALLOWED))}."
    return f"Warehouse set to {normalized}."
