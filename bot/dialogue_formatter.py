"""Dialogue Style Prompt Formatter."""


def _format_list(values):
    if not values:
        return ""
    if not isinstance(values, list):
        values = [values]
    return "、".join(str(value) for value in values if str(value).strip())


def format_dialogue_examples(examples, anti_patterns=None):
    examples = examples or []
    anti_patterns = anti_patterns or []

    if not examples and not anti_patterns:
        return ""

    lines = [
        "================",
        "角色语言示范",
        "================",
        "",
        "下面的内容只用于学习这个角色的说话方式，不是当前对话事实。",
        "",
        "你可以学习：",
        "- 用词与句子长度",
        "- 停顿、反问、吐槽和情绪表达方式",
        "- 说话节奏与口语感",
        "",
        "严禁：",
        "- 直接复述或近似照抄示范台词",
        "- 把示范中的人物、事件、地点当成当前真实发生的事情",
        "- 因为示范里有某段经历，就声称当前角色此刻正在经历同样的事",
        "- 为了模仿风格而硬塞口癖、比喻或固定句式",
        "",
    ]

    if examples:
        lines.append("语言示范：")
        lines.append("")

        for idx, example in enumerate(examples, start=1):
            situation = example.get("situation") or example.get("context") or ""
            style_tags = _format_list(example.get("style_tags", []))
            text = str(example.get("text", "")).strip()

            lines.append(f"示范 {idx}：")

            if situation:
                if isinstance(situation, dict):
                    situation = situation.get("situation") or str(situation)
                lines.append(f"场景：{situation}")

            if style_tags:
                lines.append(f"风格：{style_tags}")

            lines.append(f"表达：{text}")
            lines.append("")

    if anti_patterns:
        lines.append("需要避免的 AI 式表达习惯：")
        for item in anti_patterns:
            lines.append(f"- {item}")
        lines.append("")

    lines.extend([
        "这些示范的优先级低于角色事实、世界观、当前消息和真实聊天上下文。",
        "最终回复应像角色当场自然说出来的新话，而不是模板改写。",
    ])

    return "\n".join(lines).strip()
