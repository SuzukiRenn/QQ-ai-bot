from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from .adapters.onebot_adapter import (
    router as onebot_router
)
from .message_handler import handle_message



app = FastAPI()
app.include_router(
    onebot_router
)

from .runtime import init_runtime


init_runtime()


class ChatRequest(BaseModel):

    user_id: str

    message: str

    group_id: Optional[str] = None



@app.get("/")
def home():

    return {
        "status":"running"
    }



@app.post("/chat")
def chat_api(req: ChatRequest):

    result = handle_message(
        req.user_id,
        req.message,
        req.group_id
    )

    return {
        "action": result.action,
        "message": result.content,
        "character_id": result.character_id,
        "behavior": result.behavior,
        "priority": result.priority,
        "should_send": result.should_send
    }