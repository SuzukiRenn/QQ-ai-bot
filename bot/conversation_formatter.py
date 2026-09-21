def format_conversation_messages(
    messages,
    limit=10
):

    messages = list(
        messages
    )[-limit:]


    lines = []


    for item in messages:

        sender_type = item.get(
            "sender_type",
            "user"
        )

        user_id = item.get(
            "user_id",
            "unknown"
        )

        message = item.get(
            "message",
            ""
        )


        if sender_type == "character":

            prefix = (
                f"[角色 {user_id}]"
            )

        else:

            prefix = (
                f"[群成员 {user_id}]"
            )


        lines.append(
            f"{prefix}: {message}"
        )


    return "\n".join(
        lines
    )