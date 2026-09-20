"""
Emotion Engine

负责：
1. 从角色经历中计算长期情绪倾向
2. 合并记忆产生的情绪影响

不负责：
- 用户实时互动情绪
- 消息触发情绪变化
"""


def calculate_memory_emotion(memories):

    """
    根据 memories.yaml 中的
    emotional_impact

    计算角色长期情绪倾向
    """


    emotion_profile = {}


    if not memories:

        return emotion_profile



    memory_list = memories.get(
        "memories",
        []
    )



    for memory in memory_list:


        impact = memory.get(
            "emotional_impact",
            {}
        )


        if not impact:

            continue



        for emotion, value in impact.items():


            if emotion not in emotion_profile:

                emotion_profile[emotion] = 0



            emotion_profile[emotion] += value



    return emotion_profile





def normalize_emotion_profile(profile):

    """
    防止长期积累超过范围

    例如：

    nostalgia:
    300

    转换为：

    nostalgia:
    100

    """


    result = {}


    for emotion, value in profile.items():


        result[emotion] = min(
            value,
            100
        )


    return result





def build_long_term_emotion(memories):

    """
    对外接口

    memories.yaml

        ↓

    长期情绪画像
    """


    profile = calculate_memory_emotion(
        memories
    )


    return normalize_emotion_profile(
        profile
    )