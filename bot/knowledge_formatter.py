# bot/knowledge_formatter.py


def format_lore(lore):
    """
    世界观知识格式化
    """

    if not lore:
        return ""


    result = []

    world = lore.get(
        "world",
        {}
    )


    if world:

        name = world.get(
            "name"
        )

        description = world.get(
            "description",
            ""
        )


        if name:

            result.append(
                f"世界名称：{name}"
            )


        if description:

            result.append(
                f"世界描述：{description}"
            )


        secret = world.get(
            "secret"
        )

        if secret:

            result.append(
                f"隐藏信息：{secret}"
            )


    rules = lore.get(
        "rules",
        []
    )


    if rules:

        result.append(
            "\n世界规则："
        )


        for rule in rules:

            result.append(
                f"- {rule}"
            )


    locations = lore.get(
        "locations",
        {}
    )


    if locations:

        result.append(
            "\n重要地点："
        )


        for location_id, info in locations.items():

            location_name = info.get(
                "name",
                location_id
            )


            result.append(
                f"- {location_name}: {info.get('description','')}"
            )


    culture = lore.get(
        "culture"
    )


    if culture:

        result.append(
            "\n文化背景："
        )


        if isinstance(
            culture,
            dict
        ):

            result.append(
                culture.get(
                    "description",
                    ""
                )
            )

        else:

            result.append(
                str(culture)
            )


    return "\n".join(result)





def format_relationships(data):
    """
    角色世界关系格式化
    """

    if not data:
        return ""


    result = []


    relationships = data.get(
        "relationships",
        {}
    )


    characters = relationships.get(
        "characters",
        {}
    )


    for character_id, info in characters.items():

        result.append(
            f"{info.get('name', character_id)}:"
        )


        result.append(
            f"- 关系：{info.get('relationship', '')}"
        )


        result.append(
            f"- 态度：{info.get('attitude', '')}"
        )


        history = info.get(
            "history",
            ""
        )


        if history:

            result.append(
                f"- 经历：{history}"
            )


        result.append("")


    return "\n".join(result)




def format_events(events):

    if not events:
        return ""


    result = []


    for event in events.get(
        "events",
        []
    ):

        result.append(
            f"【{event.get('title','')}】"
        )


        result.append(
            event.get(
                "description",
                ""
            )
        )


        if event.get(
            "importance"
        ):

            result.append(
                f"重要程度：{event['importance']}"
            )


    return "\n".join(result)





def format_memories(memories):
    """
    角色经历格式化
    """

    if not memories:
        return ""


    result = []


    for memory in memories.get(
        "memories",
        []
    ):

        title = memory.get(
            "title",
            ""
        )


        description = memory.get(
            "description",
            ""
        )


        result.append(
            f"【{title}】"
        )


        if description:

            result.append(
                description
            )


        tags = memory.get(
            "tags",
            []
        )


        if tags:

            result.append(
                f"相关标签：{', '.join(tags)}"
            )


        emotional_impact = memory.get(
            "emotional_impact",
            {}
        )


        if emotional_impact:

            result.append(
                "情绪影响："
            )


            for emotion, value in emotional_impact.items():

                result.append(
                    f"- {emotion}: {value}"
                )


        importance = memory.get(
            "importance"
        )


        if importance:

            result.append(
                f"重要程度：{importance}"
            )


        result.append(
            ""
        )


    return "\n".join(result)