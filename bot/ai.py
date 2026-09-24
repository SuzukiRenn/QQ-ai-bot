import os

from dotenv import load_dotenv

from .llm import client

from .prompt import build_prompt

from .memory_retriever import retrieve_memories

from .dialogue_retriever import (
    retrieve_dialogue_examples,
    get_anti_patterns,
)

from .proactive_prompt import (
    build_proactive_prompt
)

load_dotenv()


def ask_ai(
        
        
    history,
    user_profile=None,
    emotion_context=None,
    relationship=None,
    relationship_level=None,
    character_context=None,
    message_context=None,
    reply_type=None,
    scene_type=None
):


    character = character_context["character"]


    knowledge = {

        "lore":
            character_context.get(
                "lore",
                {}
            ),


        "relationships":
            character_context.get(
                "relationships",
                {}
            ),


        "events":
            character_context.get(
                "events",
                {}
            ),


        "memories":
            character_context.get(
                "memories",
                {}
            ),


        "reply_behavior":
            character_context.get(
                "reply_behavior",
                {}
            )

    }



    related_memories = retrieve_memories(

        history[-1]["content"],

        knowledge.get(
            "memories",
            {}
        )

    )


    dialogue_style = character_context.get(
        "dialogue_style",
        {}
    )


    selected_dialogue_examples = retrieve_dialogue_examples(

        history[-1]["content"] if history else "",

        dialogue_style,

        reply_type=reply_type,

        emotion=(
            emotion_context.get("mood")
            if emotion_context
            else None
        ),

        scene=scene_type,

        relationship_level=relationship_level,

        top_k=4

    )


    dialogue_anti_patterns = get_anti_patterns(
        dialogue_style
    )



    system_prompt = build_prompt(

        character,

        knowledge,

        user_profile,

        related_memories,


        emotion_context=emotion_context,


        relationship=relationship,


        relationship_level=relationship_level,


        message_context=message_context,


        reply_type=reply_type,

        dialogue_examples=selected_dialogue_examples,

        dialogue_anti_patterns=dialogue_anti_patterns

    )



    response = client.chat.completions.create(

        model="deepseek-chat",

        messages=[

            {

                "role": "system",

                "content": system_prompt

            }

        ]

        +

        history

    )


    return response.choices[0].message.content

def ask_proactive_ai(
    character_context,
    scene_context,
    conversation_state,
    behavior="chat"
):


    system_prompt = build_proactive_prompt(

        character_context=character_context,

        scene_context=scene_context,

        conversation_state=conversation_state,

        behavior=behavior

    )


    response = client.chat.completions.create(

        model="deepseek-chat",

        messages=[

            {
                "role": "system",
                "content": system_prompt
            },

            {
                "role": "user",
                "content":
                    "根据当前群聊上下文，"
                    "生成一次自然的主动群聊发言。"
            }

        ]

    )


    content = (
        response
        .choices[0]
        .message
        .content
        .strip()
    )

    # 清理模型偶尔产生的孤立结尾引号
    if (
        content.endswith('"')
        and content.count('"') % 2 == 1
    ):
        content = content[:-1].rstrip()


    # 模型仍然拥有最后一次保持沉默的机会

    if content == "__SILENCE__":

        return None


    return content

def ask_llm(
    prompt
):

    response = client.chat.completions.create(

        model="deepseek-chat",

        messages=[

            {
                "role":"user",
                "content":prompt
            }

        ]

    )


    return response.choices[0].message.content