import yaml
import os


_character_cache = {}


def load_yaml(path):

    if not os.path.exists(path):
        return {}

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as f:
        return yaml.safe_load(f)



def load_character_knowledge(character_id):

    if character_id in _character_cache:
        return _character_cache[character_id]


    base = f"characters/{character_id}"


    knowledge = {

        "lore":
            load_yaml(
                f"{base}/lore.yaml"
            ),

        "relationships":
            load_yaml(
                f"{base}/relationships.yaml"
            ),

        "events":
            load_yaml(
                f"{base}/events.yaml"
            ),

        "memories":
            load_yaml(
                f"{base}/memories.yaml"
            ),

        "reply_behavior":
            load_yaml(
                f"{base}/reply_behavior.yaml"
            )

    }


    _character_cache[character_id] = knowledge


    return knowledge