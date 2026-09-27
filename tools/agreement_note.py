"""Agreement note tool for order creation."""

from langchain_core.tools import tool


@tool
def get_agreement_note() -> str:
    """Return the shipping agreement note the user must confirm before creating an order.

    Call this when starting an order, before asking the user to confirm the shipping note.
    """
    return (
        "Important shipping note\n"
        "1. All packages to be consolidated must be in the same order. "
        "2. You must select the Verify & Consolidate option to have your order consolidated.\n"
        "3. Packages not added to an order within 14 days of arrival at our warehouse "
    )
