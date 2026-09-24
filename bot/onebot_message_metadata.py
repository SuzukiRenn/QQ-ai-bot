# ============================================================
# OneBot Message Metadata
# ============================================================


def extract_message_metadata(event):
    """
    从 OneBot 结构化 message segments 中提取确定性 target 信号。

    当前处理：

    - at_bot: 明确 @ 当前机器人 QQ
    - at_other_users: 明确 @ 其他群成员
    - at_all: @全体成员
    - reply_message_id: 被引用/回复消息的 OneBot message_id

    reply_to_bot 不能只靠 reply 段本身判断：
    reply 段只携带被回复消息的 id，必须再通过 get_msg 查询
    原消息 sender，随后由 Adapter 写回 reply_to_bot。

    raw_message 只适合展示文本，不能可靠表达 @ / reply 的目标。
    target 判断应优先使用这里的结构化信号。
    """

    self_id = str(event.get("self_id") or "")
    segments = event.get("message")

    metadata = {
        "at_bot": False,
        "at_other_users": [],
        "at_all": False,
        "reply_message_id": None,
        "reply_sender_user_id": None,
        "reply_to_bot": False,
        "reply_to_other_user": False,
    }

    if not isinstance(segments, list):
        return metadata

    seen_other = set()

    for segment in segments:
        if not isinstance(segment, dict):
            continue

        segment_type = segment.get("type")
        data = segment.get("data") or {}

        # =====================
        # @ Segment
        # =====================

        if segment_type == "at":
            qq = str(data.get("qq") or "").strip()

            if not qq:
                continue

            if qq == "all":
                metadata["at_all"] = True
                continue

            if self_id and qq == self_id:
                metadata["at_bot"] = True
                continue

            if qq not in seen_other:
                seen_other.add(qq)
                metadata["at_other_users"].append(qq)

            continue

        # =====================
        # Reply Segment
        # =====================
        #
        # OneBot/NapCat 接收 reply 段时通常提供：
        #
        # {"type": "reply", "data": {"id": "..."}}
        #
        # 某些实现/路径也可能出现 seq，保留兼容兜底。
        # 一条普通消息只需要使用第一个有效 reply 段。
        # =====================

        if (
            segment_type == "reply"
            and metadata["reply_message_id"] is None
        ):
            reply_id = data.get("id")

            if reply_id in (None, ""):
                reply_id = data.get("seq")

            if reply_id not in (None, ""):
                metadata["reply_message_id"] = str(reply_id).strip()

    return metadata


def extract_reply_sender_user_id(response):
    """
    从 OneBot get_msg 响应中提取原消息发送者 QQ。

    标准 get_msg 响应的发送者位于：

        response["data"]["sender"]["user_id"]

    解析失败时返回 None；调用方应选择安全降级，而不是猜测。
    """

    if not isinstance(response, dict):
        return None

    status = response.get("status")
    retcode = response.get("retcode")

    if status not in (None, "ok"):
        return None

    if retcode not in (None, 0):
        return None

    data = response.get("data")

    if not isinstance(data, dict):
        return None

    sender = data.get("sender")

    if not isinstance(sender, dict):
        return None

    user_id = sender.get("user_id")

    if user_id in (None, ""):
        return None

    user_id = str(user_id).strip()

    return user_id or None


def apply_reply_sender(
    metadata,
    self_id,
    reply_sender_user_id
):
    """
    将 get_msg 得到的发送者信息写回 message_metadata。

    返回新的 dict，避免调用方意外共享/修改旧对象。
    """

    result = dict(metadata or {})

    result.setdefault("reply_message_id", None)
    result.setdefault("reply_sender_user_id", None)
    result.setdefault("reply_to_bot", False)
    result.setdefault("reply_to_other_user", False)

    sender_id = str(reply_sender_user_id or "").strip()
    bot_id = str(self_id or "").strip()

    if not sender_id:
        return result

    result["reply_sender_user_id"] = sender_id
    result["reply_to_bot"] = bool(
        bot_id
        and sender_id == bot_id
    )
    result["reply_to_other_user"] = bool(
        bot_id
        and sender_id != bot_id
    )

    return result
