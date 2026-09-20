import redis
import json
import os


client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    decode_responses=True
)


def save_message(
    character_id,
    user_id,
    role,
    content
):

    data = {

        "role": role,

        "content": content

    }


    client.rpush(
        f"chat:{character_id}:{user_id}",

        json.dumps(
            data,
            ensure_ascii=False
        )
    )



def get_history(
    character_id,
    user_id
):

    messages = client.lrange(

        f"chat:{character_id}:{user_id}",

        -10,

        -1

    )


    return [

        json.loads(item)

        for item in messages

    ]