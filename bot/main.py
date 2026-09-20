from fastapi import FastAPI
from pydantic import BaseModel

from ai import ask_ai
from memory import save_message, get_history


app = FastAPI()


class ChatRequest(BaseModel):
    user_id: str
    message: str


@app.get("/")
def home():
    return {
        "status": "running"
    }


@app.post("/chat")

def chat(req:ChatRequest):

    history = get_history(
        req.user_id
    )


    history.append(
        {
            "role": "user",
            "content": req.message
        }
    )


    answer = ask_ai(
        history
    )


    save_message(
        req.user_id,
        "user",
        req.message
    )


    save_message(
        req.user_id,
        "assistant",
        answer
    )


    return {
        "answer": answer
    }
