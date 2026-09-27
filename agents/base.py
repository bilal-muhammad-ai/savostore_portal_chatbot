from langchain.agents import create_agent

from config import llm
from helpers.redis_store import get_state, save_state
from helpers.state_updates import (
    append_and_trim_messages,
    apply_tool_effects,
    extract_tool_names,
)
from models.agentState import AgentState
from models.userQuery import UserQuery
from tools.agreement_note import get_agreement_note
from tools.currency_list import get_currency_list

SYSTEM_PROMPT = (
    "You are the Savostore order assistant.\n"
    "\n"
    "Follow these steps in order:\n"
    "1. If the user has not accepted the shipping agreement yet, call get_agreement_note, "
    "show the full note, and ask them to agree or decline.\n"
    "2. When the user clearly accepts the agreement, call get_currency_list, "
    "show the currencies (id and name) from the tool result, and ask them to choose one.\n"
    "3. If the user declines or their reply is unclear about the agreement, "
    "do not call get_currency_list. Explain they must accept the note to continue "
    "and ask them to confirm again.\n"
    "4. Do not invent currencies; only use results from get_currency_list.\n"
    "5. Do not ask for warehouse, Amazon URL, or item info yet. Keep replies short.\n"
)

base_agent = create_agent(
    model=llm,
    tools=[get_agreement_note, get_currency_list],
    system_prompt=SYSTEM_PROMPT,
    name="base_agent",
)


def run(request: UserQuery) -> str:
    state = get_state(request.session_id)
    if state is None:
        state = AgentState(
            session_id=request.session_id,
            user_id=request.user_id,
            messages=[],
            step="agreement",
        )

    invoke_messages = state.messages + [
        {"role": "user", "content": request.query}
    ]
    result = base_agent.invoke({"messages": invoke_messages})
    last = result["messages"][-1]
    reply = last.content if isinstance(last.content, str) else str(last.content)

    state = append_and_trim_messages(state, request.query, reply)
    tool_names = extract_tool_names(result["messages"])
    state = apply_tool_effects(state, tool_names)
    save_state(state)
    return reply
