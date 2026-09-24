from .runtime import character_manager

from .conversation_state import (
    conversation_state
)


from .character_manager import (
    get_character_id
)


from .relationship import (
    get_relationship,
    update_relationship,
    get_relationship_level
)


from .reply_decision import (
    should_reply
)


from .message_analyzer import (
    analyze_message
)


from .emotion import (
    decay_emotion
)


from .emotion_context import (
    build_emotion_context
)


from .relationship_trigger import (
    analyze_relationship_change
)


from .user_profile import (
    get_user_profile,
    update_user_profile
)


from .profile_extractor import (
    extract_profile
)


from .memory import (
    get_history,
    save_message
)


from .memory_retriever import (
    retrieve_memories
)


from .emotion_trigger import (
    analyze_emotion_change
)


from .ai import (
    ask_ai
)

from .media.media_formatter import format_media_context



def chat(
    user_id,
    message,
    group_id=None,
    message_metadata=None,
    media_context=None
):


    # =====================
    # 1. 获取角色
    # =====================

    character_id = get_character_id(
        user_id,
        group_id
    )


    character_context = (
        character_manager.get(
            character_id
        )
    )


    if not character_context:

        raise Exception(
            f"Character not loaded: "
            f"{character_id}"
        )


    print(
        "当前角色:",
        character_id
    )



    # =====================
    # 2. 构建 Knowledge Context
    # =====================

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



    # =====================
    # 3. 情绪衰减
    # =====================

    decay_emotion(
        character_id,
        user_id
    )



    # =====================
    # 4. 用户资料
    # =====================

    profile_update = extract_profile(
        message
    )


    if profile_update:

        update_user_profile(
            user_id,
            profile_update
        )


    profile = get_user_profile(
        user_id
    )



    # =====================
    # 5. 关系系统
    # =====================

    relationship = get_relationship(
        character_id,
        user_id
    )


    relationship_level = (
        get_relationship_level(
            relationship
        )
    )


    relationship_result = (
        analyze_relationship_change(
            message
        )
    )


    relationship_change = (
        relationship_result.get(
            "relationship_change",
            {}
        )
    )


    if relationship_change:

        update_relationship(
            character_id,
            user_id,
            relationship_change
        )



    # =====================
    # 6. 聊天历史
    # =====================

    history = get_history(
        character_id,
        user_id
    )


    history.append(
        {
            "role": "user",
            "content": message
        }
    )



    # =====================
    # 7. 记忆检索
    # =====================

    related_memories = retrieve_memories(

        message,

        knowledge.get(
            "memories",
            {}
        )

    )



    # =====================
    # 8. 当前 Emotion Context
    # =====================

    emotion_context = (
        build_emotion_context(
            character_id,
            user_id
        )
    )



    # =====================
    # 9. 消息理解
    # =====================

    chat_type = (
        "group"
        if group_id
        else "private"
    )


    print(
        "聊天类型:",
        chat_type
    )


    character_meta = (

        character_context[
            "character"
        ][
            "meta"
        ]

    )


    # =====================
    # 9.1 获取最近群聊上下文
    # =====================
    #
    # message_handler 会在调用 chat() 前，
    # 先把当前消息写入 ConversationState。
    #
    # 因此这里 recent_messages 中已经包含：
    #
    # 用户上一条
    # ↓
    # 角色上一条回复
    # ↓
    # 用户当前消息
    #
    # 可以用于判断连续对话。
    # =====================

    recent_messages = []


    if group_id:

        conversation = (
            conversation_state.get(
                group_id
            )
        )


        recent_messages = list(

            conversation.get(
                "messages",
                []
            )

        )[-8:]


    # =====================
    # 9.2 Message Analyzer
    # =====================

    message_context = analyze_message(

        message,

        character_name=(
            character_meta.get(
                "name"
            )
        ),

        character_aliases=(
            character_meta.get(
                "aliases",
                []
            )
        ),

        chat_type=chat_type,

        recent_messages=
            recent_messages,

        current_user_id=
            user_id,

        character_id=
            character_id,

        message_metadata=
            message_metadata

    )


    print(
        "消息理解:",
        message_context
    )



    # =====================
    # 10. 回复决策
    # =====================

    decision = should_reply(

        message,

        relationship,

        emotion_context,

        message_context,

        chat_type=chat_type

    )


    reply_type = decision.get(
        "reply_type",
        "answer"
    )


    print(
        "回复决策:",
        decision
    )


    if not decision.get(
        "should_reply",
        True
    ):

        return None



    # =====================
    # 11. AI 回复
    # =====================

    answer = ask_ai(

        history,

        user_profile=profile,

        relationship=relationship,

        relationship_level=
            relationship_level,

        emotion_context=
            emotion_context,

        character_context=
            character_context,

        message_context=
            message_context,

        reply_type=
            reply_type,

        scene_type=(
            "group_chat"
            if chat_type == "group"
            else "private_chat"
        )

    )



    # =====================
    # 12. 保存记录
    # =====================

    save_message(

        character_id,

        user_id,

        "user",

        message

    )


    save_message(

        character_id,

        user_id,

        "assistant",

        answer

    )



    return answer