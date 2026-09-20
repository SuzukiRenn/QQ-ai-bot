import os

from openai import OpenAI

from character import load_character
from prompt import build_prompt


character = load_character(
    "characters/cat.yaml"
)

SYSTEM_PROMPT = build_prompt(character)


client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)


def ask_ai(history):

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            }
        ]
        + history
    )

    return response.choices[0].message.content
