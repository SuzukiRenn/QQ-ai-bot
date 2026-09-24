"""
Dialogue Style Retriever v1

从角色的 dialogue_examples.yaml 中挑选与当前语境最接近的语言示范。

这一层只用于“怎么说”，不能提供新的世界观事实、记忆或人物关系。
"""


def _as_list(value):
    if value is None:
        return []
    if isinstance(value, (list, tuple, set)):
        return [str(item).strip() for item in value if str(item).strip()]
    text = str(value).strip()
    return [text] if text else []


def _normalize(value):
    return str(value or "").strip().lower()


def _matches(value, candidates):
    target = _normalize(value)
    values = {_normalize(item) for item in _as_list(candidates)}

    if not values:
        return False

    if "any" in values or "*" in values:
        return True

    return bool(target and target in values)


def _unwrap_dialogue_style(dialogue_style):
    if not isinstance(dialogue_style, dict):
        return {}

    wrapped = dialogue_style.get("dialogue_style")
    if isinstance(wrapped, dict):
        return wrapped

    return dialogue_style


def get_anti_patterns(dialogue_style):
    style = _unwrap_dialogue_style(dialogue_style)
    return _as_list(style.get("anti_patterns", []))


def retrieve_dialogue_examples(
    query,
    dialogue_style,
    reply_type=None,
    emotion=None,
    scene=None,
    relationship_level=None,
    top_k=4,
):
    """
    使用轻量、确定性的打分检索语言示范。

    评分：
    - reply_type 精确匹配 +5（若示例声明了不匹配的 reply_type，则跳过）
    - emotion 精确匹配 +3
    - scene 精确匹配 +2
    - relationship 精确匹配 +1
    - keyword 在当前消息中命中，每个 +1，最多 +4
    - any / * 通用示例 +0.5

    不调用 LLM，不依赖向量数据库。
    """

    style = _unwrap_dialogue_style(dialogue_style)
    examples = style.get("examples", [])

    if not isinstance(examples, list) or not examples:
        return []

    query_text = _normalize(query)
    scored = []

    for index, example in enumerate(examples):
        if not isinstance(example, dict):
            continue

        text = str(example.get("text", "")).strip()
        if not text:
            continue

        declared_reply_types = _as_list(example.get("reply_type"))

        # reply_type 是最强语义约束。
        # 如果示例明确声明了 reply_type，但和当前类型不一致，直接跳过。
        if declared_reply_types:
            normalized_types = {_normalize(item) for item in declared_reply_types}
            is_generic = "any" in normalized_types or "*" in normalized_types

            if reply_type and not is_generic and not _matches(reply_type, declared_reply_types):
                continue

        score = 0.0

        if _matches(reply_type, declared_reply_types):
            normalized_types = {_normalize(item) for item in declared_reply_types}
            if "any" in normalized_types or "*" in normalized_types:
                score += 0.5
            else:
                score += 5.0

        if _matches(emotion, example.get("emotion")):
            score += 3.0

        if _matches(scene, example.get("scene")):
            score += 2.0

        if _matches(relationship_level, example.get("relationship")):
            score += 1.0

        keyword_hits = 0
        for keyword in _as_list(example.get("keywords")):
            normalized_keyword = _normalize(keyword)
            if normalized_keyword and normalized_keyword in query_text:
                keyword_hits += 1

        score += min(keyword_hits, 4)

        # 没有任何上下文标签的示例视为通用风格示例，给一个很小的基础分。
        has_constraints = any(
            _as_list(example.get(field))
            for field in (
                "reply_type",
                "emotion",
                "scene",
                "relationship",
                "keywords",
            )
        )

        if not has_constraints:
            score += 0.25

        if score <= 0:
            continue

        scored.append((score, index, example))

    scored.sort(key=lambda item: (-item[0], item[1]))

    return [
        item[2]
        for item in scored[:max(0, int(top_k))]
    ]
