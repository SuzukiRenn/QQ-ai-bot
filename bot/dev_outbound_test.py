from .runtime import init_runtime, runtime
from .message_handler import handle_message
from .outbound_lifecycle import commit_sent_message


GROUP_ID = "90001"


def show_result(title, result):

    print()
    print("=" * 60)
    print(title)
    print("=" * 60)

    print(
        {
            "action": result.action,
            "content": result.content,
            "character_id": result.character_id,
            "behavior": result.behavior,
            "priority": result.priority,
            "should_send": result.should_send
        }
    )


def main():

    init_runtime()


    # =====================
    # 第 1 条
    # 上下文不足，应继续潜水
    # =====================

    result1 = handle_message(

        user_id="user_a",

        group_id=GROUP_ID,

        message="李兆基昨天打王者又冲进去了哈哈。"

    )


    show_result(
        "第1条消息",
        result1
    )


    if result1.should_send:

        commit_sent_message(
            GROUP_ID,
            result1
        )


    # =====================
    # 第 2 条
    # 理论上可能触发主动发言
    # =====================

    result2 = handle_message(

        user_id="user_b",

        group_id=GROUP_ID,

        message="他那波操作真的给我看笑了。"

    )


    show_result(
        "第2条消息",
        result2
    )


    if result2.should_send:

        print()
        print(
            "模拟 QQ 发送成功：",
            result2.content
        )

        commit_sent_message(
            GROUP_ID,
            result2
        )


    # =====================
    # 检查角色自己的消息
    # 是否已经写回群聊状态
    # =====================

    print()
    print("=" * 60)
    print("发送成功后的 ConversationState")
    print("=" * 60)

    state = runtime.conversation_state.get(
        GROUP_ID
    )

    for item in state["messages"]:

        print(
            item
        )


    # =====================
    # 第 3 条
    # 刚说完话，应进入 cooldown
    # =====================

    result3 = handle_message(

        user_id="user_c",

        group_id=GROUP_ID,

        message="今天要是还这么玩估计又得被我们笑一天。"

    )


    show_result(
        "第3条消息",
        result3
    )

    # =====================
    # 第 3 条如果成功生成主动消息
    # 模拟 QQ 发送成功
    # =====================

    if result3.should_send:

        print()
        print(
            "模拟 QQ 发送成功：",
            result3.content
        )

        commit_sent_message(
            GROUP_ID,
            result3
        )


    # =====================
    # 第 4 条
    # 应该在 Cheap Precheck 阶段
    # 直接被 cooldown 拦截
    # =====================

    result4 = handle_message(

        user_id="user_d",

        group_id=GROUP_ID,

        message="哈哈哈他今天估计还得继续冲。"

    )


    show_result(
        "第4条消息",
        result4
    )


if __name__ == "__main__":

    main()