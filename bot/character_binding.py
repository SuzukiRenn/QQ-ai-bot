import os

import redis


client = redis.Redis(
    host=os.getenv(
        "REDIS_HOST",
        "localhost"
    ),
    port=int(
        os.getenv(
            "REDIS_PORT",
            6379
        )
    ),
    decode_responses=True
)


DEFAULT_CHARACTER_ID = (
    os.getenv(
        "DEFAULT_CHARACTER_ID",
        "black_cat"
    ).strip()
    or
    "black_cat"
)


def _group_key(
    group_id
):

    return (
        f"character_binding:"
        f"group:{group_id}"
    )


def get_group_character(
    group_id
):

    character_id = client.get(
        _group_key(
            group_id
        )
    )

    if character_id:

        return character_id

    return DEFAULT_CHARACTER_ID


def set_group_character(
    group_id,
    character_id
):

    client.set(
        _group_key(
            group_id
        ),
        character_id
    )


def clear_group_character(
    group_id
):

    client.delete(
        _group_key(
            group_id
        )
    )