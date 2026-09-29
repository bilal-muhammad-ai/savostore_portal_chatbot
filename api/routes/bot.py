from fastapi import APIRouter
from pydantic import BaseModel
from models.userQuery import UserQuery

from agents.base import run

router = APIRouter()


class ChatRequest(UserQuery):
    pass


@router.post("/chat")
def chat(request: ChatRequest):
    return {"message": run(request)}


@router.get("/faq")
def faq():
    return {"message": "Hello World"}