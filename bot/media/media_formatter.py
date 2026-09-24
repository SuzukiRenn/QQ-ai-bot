def format_media_context(media_context):
    """
    将 MediaContext 转换为 Prompt 可读文本。
    当前阶段只描述存在的媒体，不进行视觉识别。
    """
    if not media_context:
        return ""

    data = (
        media_context.to_dict()
        if hasattr(media_context, "to_dict")
        else media_context
    )

    lines = []

    if data.get("has_image"):
        lines.append("用户发送了一张图片。")
        lines.append("当前系统尚未分析图片内容。")

    vision = data.get("vision")
    if vision:
        lines.append("【视觉信息】")
        if vision.get("description"):
            lines.append(f"图片描述：{vision.get('description')}")
        if vision.get("objects"):
            lines.append("识别对象：" + "、".join(vision.get("objects")))

        if vision.get("scene"):
            lines.append(f"场景：{vision.get('scene')}")

        if vision.get("emotion"):
            lines.append(f"情绪：{vision.get('emotion')}")

    faces = data.get("faces", [])
    if faces:
        lines.append("用户发送了 QQ 表情。")
        for face in faces:
            lines.append(
                f"- face id: {face.get('id', '')}"
            )

    if not lines:
        return ""

    return (
        "\n【媒体信息】\n"
        + "\n".join(lines)
    )
