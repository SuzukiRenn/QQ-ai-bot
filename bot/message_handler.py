from .runtime import runtime
from .chat_service import chat
from .character_manager import get_character_id
from .ai import ask_proactive_ai
from .message_result import MessageResult


def handle_message(
    user_id,
    message,
    group_id=None,
    message_metadata=None
):

    # =====================
    # 1. 确定当前角色
    # =====================

    character_id = get_character_id(
        user_id,
        group_id
    )


    # =====================
    # 2. 更新群聊状态
    # =====================

    if group_id:

        runtime.conversation_state.update(
            group_id,
            user_id,
            message
        )

        print(
            "Conversation State Updated:",
            runtime.conversation_state.get(
                group_id
            )
        )


    # =====================
    # 3. Reactive Reply
    # =====================

    answer = chat(
        user_id,
        message,
        group_id,
        message_metadata=message_metadata
    )


    # 原有 Reactive 系统已经决定回复
    # 不再进入 Proactive 系统

    if answer is not None:

        return MessageResult(

            action="reactive",

            content=answer,

            character_id=character_id
        )


    # =====================
    # 4. 私聊不进入主动群聊系统
    # =====================

    if not group_id:

        return MessageResult(

            action="none",

            character_id=character_id
        )


    # =====================
    # 5. Proactive Target Guard
    # =====================
    #
    # 用户明确 @ 其他群成员时，
    # 这是一个强确定性“正在和别人说话”的信号。
    #
    # 即使 Reactive 已经保持沉默，
    # 也不能让 Proactive 再绕回来插话。
    #
    # 如果同一条消息同时 @ 机器人，
    # 则交给 Reactive 正常处理；
    # 这里不拦截。
    # =====================

    message_metadata = (
        message_metadata
        or {}
    )

    if (
        message_metadata.get("at_other_users")
        and not message_metadata.get("at_bot")
    ):
        print(
            "Proactive Target Guard:",
            "message explicitly @ other member(s)",
            message_metadata.get("at_other_users")
        )

        return MessageResult(
            action="none",
            character_id=character_id,
            behavior="observe",
            priority=0
        )


    # =====================
    # 6. Proactive System
    # =====================

    try:

        character_context = (
            runtime.character_manager.get(
                character_id
            )
        )


        if not character_context:

            print(
                "Proactive:"
                " character not loaded:",
                character_id
            )

            return MessageResult(

                action="none",

                character_id=character_id
            )


        state = runtime.conversation_state.get(
            group_id
        )



        # =====================
        # Cheap Proactive Precheck
        # =====================

        precheck = (
            runtime.proactive_behavior.precheck(

                character_id=character_id,

                character_package=character_context,

                group_id=group_id,

                conversation_state=state

            )
        )


        if precheck is not None:

            print(
                "主动行为预检查:",
                precheck
            )


            return MessageResult(

                action="none",

                character_id=character_id,

                behavior=precheck.get(
                    "behavior"
                ),

                priority=precheck.get(
                    "priority",
                    0
                )
            )

        # =====================
        # 6. 场景分析
        # =====================

        scene_context = (
            runtime.scene_analyzer.analyze(
                state,
                character_context
            )
        )


        print(
            "场景分析:",
            scene_context
        )


        # =====================
        # 7. 主动行为决策
        # =====================

        decision = (
            runtime.proactive_behavior.decide(

                character_id=character_id,

                scene_context=scene_context,

                character_package=character_context,

                group_id=group_id,

                conversation_state=state

            )
        )


        print(
            "主动行为决策:",
            decision
        )


        # =====================
        # 8. 不主动发言
        # =====================

        if not decision.get(
            "should_speak",
            False
        ):

            return MessageResult(

                action="none",

                character_id=character_id,

                behavior=decision.get(
                    "behavior"
                ),

                priority=decision.get(
                    "priority",
                    0
                )
            )


        # =====================
        # 9. 生成主动发言
        # =====================

        print(
            "[Proactive Preview]"
            " 角色决定尝试生成主动发言。"
        )


        proactive_message = ask_proactive_ai(

            character_context=character_context,

            scene_context=scene_context,

            conversation_state=state,

            behavior=decision.get(
                "behavior",
                "chat"
            )

        )


        # =====================
        # 10. 模型最终选择沉默
        # =====================

        if not proactive_message:

            print(
                "主动发言预览:"
                " 模型最终选择保持沉默。"
            )


            return MessageResult(

                action="none",

                character_id=character_id,

                behavior=decision.get(
                    "behavior"
                ),

                priority=decision.get(
                    "priority",
                    0
                )
            )


        # =====================
        # 11. 主动消息生成成功
        # =====================

        print(
            "主动发言预览:",
            proactive_message
        )


        return MessageResult(

            action="proactive",

            content=proactive_message,

            character_id=character_id,

            behavior=decision.get(
                "behavior"
            ),

            priority=decision.get(
                "priority",
                0
            )
        )


    except Exception as e:

        # Proactive 系统失败不能影响正常聊天主流程

        print(
            "Proactive Error:",
            repr(e)
        )


        return MessageResult(

            action="none",

            character_id=character_id
        )