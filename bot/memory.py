import redis
import json


client = redis.Redis(
    host="redis",
    port=6379,
    decode_responses=True
)


def save_message(user_id, role, content):

    data = {
        "role": role,
        "content": content
    }

    client.rpush(
        f"chat:{user_id}",
        json.dumps(data, ensure_ascii=False)
    )


def get_history(user_id):

    messages = client.lrange(
        f"chat:{user_id}",
        -10,
        -1
    )

    return [
        json.loads(item)
        for item in messages
    ]
