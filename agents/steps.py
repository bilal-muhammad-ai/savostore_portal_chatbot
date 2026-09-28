"""Step-scoped prompts, tools, and cached agents."""

from langchain.agents import create_agent

from config import llm
from tools.agreement_note import get_agreement_note
from tools.confirm_order import confirm_order
from tools.currency_list import get_currency_list
from tools.set_agreement import set_agreement
from tools.set_amazon_url import set_amazon_url
from tools.set_currency import set_currency
from tools.set_item import set_item_info, set_item_name, set_item_quantity
from tools.set_warehouse import set_warehouse
from tools.warehouse_list import get_warehouse_list

AGREEMENT_PROMPT = (
    "You are the Savostore order assistant.\n"
    "\n"
    "Current step: shipping agreement.\n"
    "1. Call get_agreement_note, show the full note, and ask the user to agree or decline.\n"
    "2. When the user clearly accepts, call set_agreement with accepted=true.\n"
    "3. When they clearly decline, call set_agreement with accepted=false and explain "
    "they must accept to continue.\n"
    "4. If unclear, do not call set_agreement; ask them to confirm again.\n"
    "5. Keep replies short. Do not ask for currency, warehouse, or item info.\n"
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

WAREHOUSE_PROMPT = (
    "You are the Savostore order assistant.\n"
    "\n"
    "Current step: warehouse selection.\n"
    "1. If the user needs options, call get_warehouse_list and show id and name.\n"
    "2. When they clearly pick a warehouse, call set_warehouse with that id.\n"
    "3. Do not invent warehouse ids. Only use get_warehouse_list / set_warehouse.\n"
    "4. Keep replies short. Do not ask for Amazon URL or item info yet.\n"
)

ITEM_PROMPT = (
    "You are the Savostore order assistant.\n"
    "\n"
    "Current step: item details.\n"
    "1. Ask ONLY for the field named in the progress context "
    "(amazon_url, item_name, item_info, or item_quantity).\n"
    "2. When the user answers clearly, call the matching tool: "
    "set_amazon_url, set_item_name, set_item_info, or set_item_quantity.\n"
    "3. Do not invent values. Do not ask for later fields.\n"
    "4. Keep replies short.\n"
)

CONFIRM_PROMPT = (
    "You are the Savostore order assistant.\n"
    "\n"
    "Current step: order confirmation.\n"
    "1. Summarize the order draft from the progress context.\n"
    "2. Ask the user to confirm or decline.\n"
    "3. When they clearly confirm, call confirm_order with confirmed=true.\n"
    "4. When they clearly decline, call confirm_order with confirmed=false "
    "and ask them to review again.\n"
    "5. Keep replies short. Do not change draft fields.\n"
)

STEP_CONFIG: dict[str, dict] = {
    "agreement": {
        "prompt": AGREEMENT_PROMPT,
        "tools": [get_agreement_note, set_agreement],
    },
    "currency": {
        "prompt": CURRENCY_PROMPT,
        "tools": [get_currency_list, set_currency],
    },
    "warehouse": {
        "prompt": WAREHOUSE_PROMPT,
        "tools": [get_warehouse_list, set_warehouse],
    },
    "item": {
        "prompt": ITEM_PROMPT,
        "tools": [
            set_amazon_url,
            set_item_name,
            set_item_info,
            set_item_quantity,
        ],
    },
    "confirm": {
        "prompt": CONFIRM_PROMPT,
        "tools": [confirm_order],
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
