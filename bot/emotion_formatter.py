# bot/emotion_formatter.py


"""
Emotion Formatter

负责：

Emotion Context

↓

自然语言描述

提供给 Prompt

"""


def emotion_name_translate(name):

    """
    情绪字段中文化
    """

    mapping = {

        "happiness": "开心",

        "sadness": "悲伤",

        "anger": "愤怒",

        "trust": "信任",

        "energy": "精力",

        "nostalgia": "怀念",

        "curiosity": "好奇心",

        "confidence": "自信"

    }


    return mapping.get(
        name,
        name
    )





def format_emotion_values(
    emotions,
    threshold=20
):

    """
    将：

    {
      nostalgia:100
    }

    转成：

    对过去经历有强烈怀念

    """

    if not emotions:

        return []


    result = []


    for key, value in emotions.items():


        if value < threshold:

            continue


        name = emotion_name_translate(
            key
        )


        if value >= 80:

            level = "很强"


        elif value >= 50:

            level = "明显"


        else:

            level = "轻微"



        result.append(
            f"- {name}{level}（{value}/100）"
        )


    return result





def format_emotion_context(
    context
):

    """
    统一 Emotion Context 格式化
    """


    if not context:

        return ""



    result = []



    # 长期倾向

    long_term = context.get(
        "long_term",
        {}
    )


    if long_term:


        result.append(
            "长期心理倾向："
        )


        result.extend(
            format_emotion_values(
                long_term
            )
        )



    # 当前状态

    current = context.get(
        "current",
        {}
    )


    if current:


        result.append(
            "\n当前情绪状态："
        )


        result.extend(
            format_emotion_values(
                current
            )
        )



    # 当前 mood

    mood = context.get(
        "mood"
    )


    if mood:


        mood_map = {

            "happy": "开心",

            "sad": "低落",

            "melancholy": "忧郁",

            "normal": "平稳"

        }


        result.append(
            f"\n当前整体状态：{mood_map.get(mood,mood)}"
        )



    return "\n".join(result)