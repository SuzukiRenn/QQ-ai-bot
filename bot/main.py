from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

from .chat_service import chat



app = FastAPI()

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
def chat_api(
    req: ChatRequest
):

    answer = chat(
        req.user_id,
        req.message,
        req.group_id
    )

    if answer is None:

        return {
            "answer": ""
        }

    return {
        "answer": answer
    }