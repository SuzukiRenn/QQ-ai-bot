import os
from .validators.package_validator import (
    validate_character_package
)



BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)


CHARACTER_DIR = os.path.join(
    BASE_DIR,
    "characters"
)

def get_valid_characters():

    """
    扫描并验证所有角色
    """

    characters = list_characters()


    valid = []


    for character_id in characters:


        result = validate_character_package(
            character_id
        )


        if result:

            valid.append(
                character_id
            )


    return valid

def list_characters():

    """
    自动扫描角色包
    """

    if not os.path.exists(
        CHARACTER_DIR
    ):
        return []


    characters = []


    for name in os.listdir(
        CHARACTER_DIR
    ):


        path = os.path.join(
            CHARACTER_DIR,
            name
        )


        if os.path.isdir(path):

            characters.append(
                name
            )


    return characters