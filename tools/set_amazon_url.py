"""Record the Amazon product URL for the order item."""

from urllib.parse import urlparse

from langchain_core.tools import tool

_AMAZON_HOST_MARKERS = ("amazon.", "amzn.")


@tool
def set_amazon_url(url: str) -> str:
    """Record the Amazon product URL. Call only when the user provides a clear product link."""
    cleaned = url.strip()
    parsed = urlparse(cleaned)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        return f"Invalid url '{url}'. Provide a full http(s) Amazon product URL."
    host = parsed.netloc.lower()
    if not any(marker in host for marker in _AMAZON_HOST_MARKERS):
        return f"Invalid url '{url}'. Host must be an Amazon domain."
    return f"Amazon URL set to {cleaned}."
