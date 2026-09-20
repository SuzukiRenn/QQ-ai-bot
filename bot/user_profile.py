import json
import os


PROFILE_FILE = "user_profiles.json"


def load_profiles():

    if not os.path.exists(PROFILE_FILE):
        return {}

    with open(
        PROFILE_FILE,
        "r",
        encoding="utf-8"
    ) as f:
        return json.load(f)



def save_profiles(profiles):

    with open(
        PROFILE_FILE,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            profiles,
            f,
            ensure_ascii=False,
            indent=2
        )



def get_user_profile(user_id):

    profiles = load_profiles()

    if user_id not in profiles:

        profiles[user_id] = {

            "name": None,

            "relationship": "stranger",

            "trust": 0,

            "likes": [],

            "dislikes": [],

            "notes": []

        }

        save_profiles(profiles)


    return profiles[user_id]



def update_user_profile(
    user_id,
    data
):

    profiles = load_profiles()

    if user_id not in profiles:
        profiles[user_id] = {}


    profiles[user_id].update(data)

    save_profiles(profiles)