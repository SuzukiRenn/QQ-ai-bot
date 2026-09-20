import yaml
import os


BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)


CHARACTER_DIR = os.path.join(
    BASE_DIR,
    "characters"
)



def load_character(character_id):

    path = os.path.join(
        CHARACTER_DIR,
        character_id,
        "card.yaml"
    )


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