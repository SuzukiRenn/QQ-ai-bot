from .runtime import runtime
from .message_result import MessageResult


def commit_sent_message(
    group_id,
    result: MessageResult
):
    """
    在消息真正发送成功之后调用。

    注意：
    生成消息成功 != 发送成功。

    只有 QQ Adapter 确认发送成功，
    才应该调用这里。
    """


    if not result:
        return False


    if not result.should_send:
        return False


    if not group_id:
        return False


    if not result.content:
        return False


    character_id = result.character_id


    if not character_id:
        return False


    # =====================
    # 1. 记录角色刚刚说过话
    # =====================
    #
    # Reactive 和 Proactive 都记录。
    #
    # 因为角色刚被动回复以后，
    # 也不应该下一秒马上又主动插话。
    # =====================

    runtime.proactive_behavior.mark_speak(
        character_id=character_id,
        group_id=group_id
    )


    # =====================
    # 2. 写回 ConversationState
    # =====================

    runtime.conversation_state.update(

        group_id=group_id,

        user_id=character_id,

        message=result.content,

        sender_type="character"
    )


    print(
        "Outbound Message Committed:",
        {
            "group_id": group_id,
            "character_id": character_id,
            "action": result.action,
            "message": result.content
        }
    )


    return True