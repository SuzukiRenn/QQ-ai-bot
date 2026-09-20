"""
Emotion Context Builder

负责：

合并：

1. 角色长期情绪倾向
   character_emotion_profile.json

2. 用户互动当前情绪
   emotion_state.json


输出统一 Emotion Context
"""


from .character_emotion import (
    get_character_emotion
)

from .emotion import (
    get_emotion,
    get_mood
)



def build_emotion_context(
    character_id,
    user_id
):


    # 长期情绪画像

    long_term_emotion = get_character_emotion(
        character_id
    )


    # 当前互动情绪

    current_emotion = get_emotion(
        character_id,
        user_id
    )


    # 当前心情判断

    mood = get_mood(
        current_emotion
    )


    return {


        "long_term": long_term_emotion,


        "current": current_emotion,


        "mood": mood

    }