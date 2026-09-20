import yaml
import os


def load_character(character_id):

    path = f"characters/{character_id}/card.yaml"


    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Character card not found: {path}"
        )


    with open(
        path,
        "r",
        encoding="utf-8"
    ) as f:

        data = yaml.safe_load(f)


    return data["character"]