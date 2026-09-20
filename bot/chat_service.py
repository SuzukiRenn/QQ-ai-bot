from character_manager import (
    get_character_id,
    get_character_context
)

from relationship import (
    get_relationship,
    update_relationship,
    get_relationship_level
)

from reply_decision import should_reply

from message_analyzer import analyze_message

from emotion import (
    decay_emotion,
    get_emotion,
    update_emotion,
    get_mood
)

from relationship_trigger import (
    analyze_relationship_change
)


from user_profile import (
    get_user_profile,
    update_user_profile
)


from profile_extractor import extract_profile


from memory import (
    get_history,
    save_message
)


from memory_retriever import retrieve_memories


from emotion_engine import calculate_memory_emotion


from emotion_trigger import analyze_emotion_change


from ai import ask_ai



def chat(
    user_id,
    message,
    group_id=None
):


    # =====================
    # 1. 获取角色
    # =====================

    character_id = get_character_id(
        user_id,
        group_id
    )


    character_context = get_character_context(
        character_id
    )


    print(
        "当前角色:",
        character_id
    )


    knowledge = character_context["knowledge"]

    # =====================
    # 2. 情绪衰减
    # =====================

    decay_emotion(
        character_id,
        user_id
    )



    # =====================
    # 3. 用户资料提取
    # =====================

    profile_update = extract_profile(
        message
    )

    relationship = get_relationship(
        character_id,
        user_id
    )

    relationship_level = get_relationship_level(
        relationship
    )


        # =====================
    # 关系变化分析
    # =====================

    relationship_result = analyze_relationship_change(
        message
    )


    relationship_change = relationship_result.get(
        "relationship_change",
        {}
    )


    if relationship_change:

        update_relationship(
            character_id,
            user_id,
            relationship_change
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
    # 4. 获取聊天历史
    # =====================

    history = get_history(
        character_id,
        user_id
    )


    history.append(
        {
            "role":"user",
            "content":message
        }
    )



    # =====================
    # 5. 角色记忆检索
    # =====================

    related_memories = retrieve_memories(
        message,
        knowledge.get(
            "memories",
            {}
        )
    )



    # =====================
    # 6. 情绪更新
    # =====================

    total_change = {}



    try:

        result = analyze_emotion_change(
            message
        )


        for k,v in result.get(
            "emotion_change",
            {}
        ).items():

            total_change[k] = (
                total_change.get(k,0)
                +
                v
            )


    except Exception:

        pass



    try:

        memory_change = calculate_memory_emotion(
            related_memories
        )


        for k,v in memory_change.items():

            total_change[k] = (
                total_change.get(k,0)
                +
                v
            )


    except Exception:

        pass



    if total_change:

        update_emotion(
            character_id,
            user_id,
            total_change
        )



    # =====================
    # 7. 当前状态
    # =====================

    emotion = get_emotion(
        character_id,
        user_id
    )


    mood = get_mood(
        emotion
    )



    # =====================
    # 8. 调用角色AI
    # =====================

    message_context = analyze_message(
        message,
        character_context["character"]["meta"]["name"]
    )


    print(
        "消息理解:",
        message_context
    )

    decision = should_reply(
        message,
        relationship,
        emotion,
        message_context
    )

    reply_type = decision.get(
    "reply_type",
    "answer"
)

    print("回复决策:", decision)

    if not decision.get(
        "should_reply",
        True
    ):

        return None

    answer = ask_ai(
        history,
        user_profile=profile,
        relationship=relationship,
        relationship_level=relationship_level,
        emotion=emotion,
        mood=mood,
        character_context=character_context,
        reply_type=reply_type 
    )



    # =====================
    # 9. 保存聊天
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