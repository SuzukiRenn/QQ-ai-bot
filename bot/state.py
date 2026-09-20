def get_user_state(user_id):

    return users.get(
        user_id,
        {
            "emotion": "平静",
            "relationship": "陌生人"
        }
    )