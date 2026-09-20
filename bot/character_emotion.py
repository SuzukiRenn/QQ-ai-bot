"""
Character Long-term Emotion Profile

负责：

1. 根据角色 memories.yaml
   生成长期情绪倾向

2. 保存角色级情绪画像


注意：

这里保存的是角色本身属性。

不是：

character_id:user_id

"""

import json
import os


from .emotion_engine import (
    build_long_term_emotion
)



PROFILE_FILE = "character_emotion_profile.json"



def load_profiles():

    if not os.path.exists(
        PROFILE_FILE
    ):

        return {}


    with open(
        PROFILE_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)





def save_profiles(data):

    with open(
        PROFILE_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2
        )





def generate_character_emotion(
    character_id,
    memories
):

    """
    根据 memories.yaml
    生成角色长期情绪
    """


    emotion_profile = build_long_term_emotion(
        memories
    )


    profiles = load_profiles()


    profiles[character_id] = emotion_profile


    save_profiles(
        profiles
    )


    return emotion_profile





def get_character_emotion(
    character_id
):

    """
    获取角色长期情绪画像
    """


    profiles = load_profiles()


    return profiles.get(
        character_id,
        {}
    )





def update_character_emotion(
    character_id,
    changes
):

    """
    更新角色长期情绪

    例如：

    新事件发生：

    nostalgia +5

    """


    profiles = load_profiles()


    state = profiles.get(
        character_id,
        {}
    )


    for key, value in changes.items():


        state[key] = max(
            0,
            min(
                100,
                state.get(
                    key,
                    0
                )
                +
                value
            )
        )


    profiles[character_id] = state


    save_profiles(
        profiles
    )


    return state