import yaml
import os


_character_cache = {}


BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)


CHARACTER_DIR = os.path.join(
    BASE_DIR,
    "characters"
)



def load_yaml(path):

    if not os.path.exists(path):
        return {}


    with open(
        path,
        "r",
        encoding="utf-8"
    ) as f:

        data = yaml.safe_load(f)


    return data or {}



def load_character_knowledge(character_id):

    if character_id in _character_cache:
        return _character_cache[character_id]


    base = os.path.join(
        CHARACTER_DIR,
        character_id
    )


    knowledge = {


        "lore":
            load_yaml(
                os.path.join(
                    base,
                    "lore.yaml"
                )
            ),



        "relationships":
            load_yaml(
                os.path.join(
                    base,
                    "relationships.yaml"
                )
            ),



        "events":
            load_yaml(
                os.path.join(
                    base,
                    "events.yaml"
                )
            ),



        "memories":
            load_yaml(
                os.path.join(
                    base,
                    "memories.yaml"
                )
            ),



        "reply_behavior":
            load_yaml(
                os.path.join(
                    base,
                    "reply_behavior.yaml"
                )
            ).get(
                "reply_behavior",
                {}
            )

    }


    _character_cache[character_id] = knowledge


    return knowledge