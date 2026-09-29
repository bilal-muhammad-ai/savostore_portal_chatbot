"""Jev intent classifier for order-wizard message routing."""

from __future__ import annotations

from typing import Literal

from langchain_typesafe import Choice, TypeSafeClassifier

from helpers.order_progress import format_progress_context
from models.agentState import AgentState

Intent = Literal["continue_order", "show_draft", "faq", "edit"]

_VALID_INTENTS: frozenset[str] = frozenset(
    ("continue_order", "show_draft", "faq", "edit")
)
_DEFAULT_INTENT: Intent = "continue_order"
_MIN_CONFIDENCE = 0.6

_INTENT_QUESTION = Choice(
    instructions=(
        "Classify the user message for a Savostore order wizard. "
        "When unsure, prefer continue_order."
    ),
    criteria={
        "continue_order": "Answering or progressing the current order step.",
        "show_draft": "Wants to see filled or missing order draft info.",
        "faq": "Side question (shipping, warehouse address, prohibited items, etc.).",
        "edit": "Wants to change a field already filled in the draft.",
    },
)

_classifier: TypeSafeClassifier | None = None


def _get_classifier() -> TypeSafeClassifier:
    """Lazy-init so missing TYPESAFE_API_KEY fails at classify time, not import."""
    global _classifier
    if _classifier is None:
        _classifier = TypeSafeClassifier()
    return _classifier


def classify_intent(query: str, state: AgentState) -> Intent:
    """Classify the user message via Jev; default to continue_order on failure."""
    progress = format_progress_context(state)
    state_text = (
        f"Savostore order wizard.\n"
        f"Current step: {state.step}\n"
        f"{progress}\n"
        f"User message: {query}"
    )
    try:
        response = _get_classifier().invoke(
            {
                "state": state_text,
                "questions": {"intent": _INTENT_QUESTION},
            }
        )
        answer = response.choices["intent"]
        intent = answer.choice
        if intent in _VALID_INTENTS and answer.confidence >= _MIN_CONFIDENCE:
            return intent  # type: ignore[return-value]
    except Exception:
        pass
    return _DEFAULT_INTENT
