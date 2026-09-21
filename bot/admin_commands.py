import os

from .runtime import runtime

from .character_binding import (
    get_group_character,
    set_group_character
)


def get_admin_ids():

    raw = os.getenv(
        "BOT_ADMIN_QQ_IDS",
        ""
    )


    return {

        item.strip()

        for item in raw.split(",")

        if item.strip()

    }


def is_admin(
    user_id
):

    return (
        str(user_id)
        in get_admin_ids()
    )


def get_character_name(
    character_id
):

    package = (
        runtime.character_manager.get(
            character_id
        )
    )


    if not package:

        return character_id


    character = package.get(
        "character",
        {}
    )


    meta = character.get(
        "meta",
        {}
    )


    name = meta.get(
        "name",
        character_id
    )


    return (
        f"{character_id}（{name}）"
    )


def handle_admin_command(
    user_id,
    group_id,
    message
):
    """
    返回：

    None:
        不是管理命令

    str:
        管理命令处理结果
    """

    text = str(
        message
    ).strip()


    # =====================
    # 是否属于管理命令
    # =====================

    is_command = (

        text == "/角色"

        or text == "/角色列表"

        or text.startswith(
            "/切换角色 "
        )

        or text.startswith(
            "/角色 "
        )

    )


    if not is_command:

        return None


    # =====================
    # 权限检查
    # =====================

    if not is_admin(
        user_id
    ):

        return (
            "⛔ 你没有管理员权限，"
            "无法执行角色管理命令。"
        )


    # =====================
    # 查看当前角色
    # =====================

    if text == "/角色":

        current = (
            get_group_character(
                group_id
            )
        )


        return (
            "当前角色："
            f"{get_character_name(current)}"
        )


    # =====================
    # 查看角色列表
    # =====================

    if text == "/角色列表":

        loaded = (
            runtime
            .character_manager
            .list_loaded()
        )


        lines = [

            "当前可用角色："

        ]


        current = (
            get_group_character(
                group_id
            )
        )


        for character_id in loaded:

            prefix = (
                "👉 "
                if character_id == current
                else "• "
            )


            lines.append(

                prefix
                +
                get_character_name(
                    character_id
                )

            )


        return "\n".join(
            lines
        )


    # =====================
    # 切换角色
    # =====================

    if text.startswith(
        "/切换角色 "
    ):

        target = (
            text[
                len("/切换角色 "):
            ].strip()
        )

    else:

        target = (
            text[
                len("/角色 "):
            ].strip()
        )


    if not target:

        return (
            "用法："
            "/切换角色 <character_id>"
        )


    loaded = (
        runtime
        .character_manager
        .list_loaded()
    )


    if target not in loaded:

        return (

            "❌ 未找到角色："
            f"{target}\n"

            "可用角色："
            + ", ".join(
                loaded
            )

        )


    old_character = (
        get_group_character(
            group_id
        )
    )


    if old_character == target:

        return (
            "当前已经是："
            f"{get_character_name(target)}"
        )


    # =====================
    # 保存群角色绑定
    # =====================

    set_group_character(
        group_id,
        target
    )


    # =====================
    # 清空群短期 ConversationState
    #
    # 避免新角色把旧角色刚才的话
    # 当成自己的历史上下文。
    # =====================

    runtime.conversation_state.clear(
        group_id
    )


    # 新角色立即可以正常工作

    runtime.proactive_behavior.clear_cooldown(
        target,
        group_id
    )


    print(
        "Character switched:",
        {
            "group_id":
                str(group_id),

            "admin_user_id":
                str(user_id),

            "from":
                old_character,

            "to":
                target
        }
    )


    return (

        "✅ 角色已切换：\n"

        f"{get_character_name(old_character)}"

        "\n→\n"

        f"{get_character_name(target)}"

    )