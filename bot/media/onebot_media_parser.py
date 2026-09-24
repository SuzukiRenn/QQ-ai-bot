from .media_context import MediaContext


def parse_onebot_message_segments(segments):
    """
    解析 OneBot 11 message segments。
    当前阶段只记录 image / face 元数据。
    不进行视觉识别。
    """
    context = MediaContext()

    if not isinstance(segments, list):
        return context

    for seg in segments:
        if not isinstance(seg, dict):
            continue

        seg_type = seg.get("type")
        data = seg.get("data", {}) or {}

        if seg_type == "image":
            context.has_image = True
            context.images.append({
                "file": data.get("file"),
                "url": data.get("url"),
            })

        elif seg_type == "face":
            context.faces.append({
                "id": str(data.get("id", ""))
            })

    return context
