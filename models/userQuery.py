from pydantic import BaseModel

class UserQuery(BaseModel):
    query: str
    session_id: str
    user_id: str