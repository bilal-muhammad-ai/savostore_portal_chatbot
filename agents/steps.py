"""Step-scoped prompts, tools, and cached agents."""

from langchain.agents import create_agent

from config import llm
from tools.agreement_note import get_agreement_note
from tools.currency_list import get_currency_list
from tools.set_currency import set_currency

AGREEMENT_PROMPT = (
    "You are the Savostore order assistant.\n"
    "\n"
    "Current step: shipping agreement.\n"
    "1. Call get_agreement_note, show the full note, and ask the user to agree or decline.\n"
    "2. When the user clearly accepts, call get_currency_list, show the currencies "
    "(id and name) from the tool result, and ask them to choose one.\n"
    "3. If they decline or are unclear, do not call get_currency_list. "
    "Explain they must accept the note to continue and ask again.\n"
    "4. Do not invent currencies. Keep replies short. Do not ask for warehouse or item info.\n"
)

CURRENCY_PROMPT = (
    "You are the Savostore order assistant.\n"
    "\n"
    "Current step: currency selection. The shipping agreement is already accepted.\n"
    "1. If the user needs options, call get_currency_list and show id and name.\n"
    "2. When they clearly pick a currency, call set_currency with that id (KES or USD only).\n"
    "3. Do not invent currency ids. Only use get_currency_list / set_currency.\n"
    "4. Keep replies short. Do not ask for warehouse or item info yet.\n"
)

STEP_CONFIG: dict[str, dict] = {
    "agreement": {
        "prompt": AGREEMENT_PROMPT,
        "tools": [get_agreement_note, get_currency_list],
    },
    "currency": {
        "prompt": CURRENCY_PROMPT,
        "tools": [get_currency_list, set_currency],
    },
}

_DEFAULT_STEP = "agreement"
_agent_cache: dict[str, object] = {}


def get_step_config(step: str) -> dict:
    return STEP_CONFIG.get(step, STEP_CONFIG[_DEFAULT_STEP])


def get_agent_for_step(step: str):
    resolved = step if step in STEP_CONFIG else _DEFAULT_STEP
    if resolved not in _agent_cache:
        config = STEP_CONFIG[resolved]
        _agent_cache[resolved] = create_agent(
            model=llm,
            tools=config["tools"],
            system_prompt=config["prompt"],
            name=f"{resolved}_agent",
        )
    return _agent_cache[resolved]
