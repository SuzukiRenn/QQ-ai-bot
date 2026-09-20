import json
import os


EMOTION_FILE = "emotion_state.json"



def load_emotions():

    if not os.path.exists(EMOTION_FILE):

        return {}


    with open(
        EMOTION_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)




def save_emotions(data):

    with open(
        EMOTION_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2
        )





def create_default_emotion():

    return {

        # 当前情绪

        "happiness": 50,

        "sadness": 0,

        "anger": 0,


        # 社交情绪

        "trust": 0,


        # 长期情绪倾向

        "nostalgia": 0,

        "curiosity": 0,

        "confidence": 0,


        # 状态

        "energy": 70

    }





def get_emotion(
    character_id,
    user_id
):

    emotions = load_emotions()


    key = f"{character_id}:{user_id}"


    if key not in emotions:

        emotions[key] = create_default_emotion()

        save_emotions(emotions)


    return emotions[key]





def update_emotion(
    character_id,
    user_id,
    changes
):

    emotions = load_emotions()


    key = f"{character_id}:{user_id}"


    state = emotions.get(
        key,
        create_default_emotion()
    )


    for key_name, value in changes.items():

        state[key_name] = max(
            0,
            min(
                100,
                state.get(
                    key_name,
                    0
                )
                +
                value
            )
        )


    emotions[key] = state


    save_emotions(emotions)


    return state





def decay_emotion(
    character_id,
    user_id
):

    emotions = load_emotions()


    key = f"{character_id}:{user_id}"


    if key not in emotions:

        return



    state = emotions[key]


    # 只衰减短期负面情绪

    decay_keys = [

        "sadness",

        "anger"

    ]


    for emotion_key in decay_keys:

        if state.get(
            emotion_key,
            0
        ) > 0:

            state[emotion_key] = max(
                0,
                state[emotion_key] - 5
            )



    emotions[key] = state


    save_emotions(emotions)


    return state





def get_mood(state):

    sadness = state.get(
        "sadness",
        0
    )


    happiness = state.get(
        "happiness",
        0
    )


    if sadness > 70:

        return "sad"



    if happiness > 70:

        return "happy"



    if sadness > 30:

        return "melancholy"



    return "normal"