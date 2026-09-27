from pydantic import BaseModel


class OrderDraft(BaseModel):
    agreement_accepted: bool | None = None
    currency_id: str | None = None  # "KES" | "USD"
    warehouse_id: str | None = None
    amazon_url: str | None = None
    item_name: str | None = None
    item_info: str | None = None
    item_quantity: int | None = None


class AgentState(BaseModel):
    session_id: str
    user_id: str
    messages: list[dict]
    step: str = "agreement"  # agreement | currency | warehouse | item | confirm | done
    order: OrderDraft = OrderDraft()
