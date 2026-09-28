"""Warehouse list tool for order creation."""

from langchain_core.tools import tool

WAREHOUSES = [
    {"id": "NBO", "name": "Nairobi"},
    {"id": "MBA", "name": "Mombasa"},
]


@tool
def get_warehouse_list() -> list[dict]:
    """Return available warehouses (id and name). Call when the user needs warehouse options."""
    return list(WAREHOUSES)
