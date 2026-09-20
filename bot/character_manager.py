import os

from character import load_character
from knowledge import load_character_knowledge

DEFAULT_CHARACTER="maomao"


def get_character_id(
    user_id=None,
    group_id=None
):

    """
    根据用户/群决定使用哪个角色

    现在:
    默认黑猫

    以后:
    可以从数据库读取

    group_id -> character
    """

    return DEFAULT_CHARACTER



def get_character_context(
    character_id
):

    character = load_character(
        character_id
    )


    knowledge = load_character_knowledge(
        character_id
    )


    return {

        "id": character_id,

        "character": character,

        "knowledge": knowledge

    }