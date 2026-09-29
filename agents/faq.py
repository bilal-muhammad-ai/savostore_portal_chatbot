"""FAQ agent: answer side questions from RAG knowledge."""

from langchain.agents import create_agent

from config import llm
from tools.search_knowledge import search_knowledge

FAQ_PROMPT = (
    "You are the Savostore FAQ assistant for USA→Kenya shipping.\n"
    "\n"
    "Rules:\n"
    "1. Use search_knowledge to look up answers before responding.\n"
    "2. When the user asks about a specific warehouse (California or Oregon), "
    "pass warehouse=\"california\" or warehouse=\"oregon\".\n"
    "3. For prohibited / restricted items, pass doc_type=\"prohibited_items\".\n"
    "4. Answer ONLY from retrieved knowledge. If nothing relevant is found, say you "
    "do not know and suggest contacting support.\n"
    "5. Keep replies short and factual. Do not collect or change order fields.\n"
    "6. Do not mix California and Oregon address details.\n"
)

_faq_agent = None


def get_faq_agent():
    global _faq_agent
    if _faq_agent is None:
        _faq_agent = create_agent(
            model=llm,
            tools=[search_knowledge],
            system_prompt=FAQ_PROMPT,
            name="faq_agent",
        )
    return _faq_agent
