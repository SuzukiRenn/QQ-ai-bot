import os
from dotenv import load_dotenv
from .llm import client

load_dotenv()

from .prompt import build_prompt
from .memory_retriever import retrieve_memories


def ask_ai(
    history,
    user_profile=None,
    emotion=None,
    mood=None,
    relationship=None,
    relationship_level=None,
    character_context=None,
    message_context=None,
    reply_type=None
):
    character = character_context["character"]
    knowledge = character_context["knowledge"]
    
    related_memories = retrieve_memories(
        history[-1]["content"],
        knowledge.get("memories")
    )
    
    system_prompt = build_prompt(
        character,
        knowledge,
        user_profile,
        related_memories,
        emotion=emotion,
        relationship=relationship,
        relationship_level=relationship_level,
        mood=mood,
        message_context=message_context,
        reply_type=reply_type
    )

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {
                "role": "system",
                "content": system_prompt
            }
        ]
        + history
    )

    return response.choices[0].message.content
