from .character_registry import (
    list_characters
)

from .character_loader import (
    load_character_package
)

from .validators.package_validator import (
    validate_character_package
)

from .character_binding import (
    get_group_character
)


class CharacterManager:


    def __init__(self):

        self.characters = {}



    def load_all_characters(self):

        """
        扫描、验证、加载所有角色
        """


        character_ids = list_characters()



        for character_id in character_ids:


            print(
                f"\nLoading character: {character_id}"
            )


            valid = validate_character_package(
                character_id
            )


            if not valid:

                print(
                    f"Skip invalid character: {character_id}"
                )

                continue



            character = load_character_package(
                character_id
            )


            self.characters[
                character_id
            ] = character



            print(
                f"✅ Loaded: {character_id}"
            )



        return self.characters





    def get(
        self,
        character_id
    ):

        """
        获取角色
        """


        return self.characters.get(
            character_id
        )





    def list_loaded(self):

        return list(
            self.characters.keys()
        )


def get_character_id(
    user_id,
    group_id=None
):

    """
    获取当前应该使用的角色。

    群聊：
        使用当前群绑定角色。

    私聊：
        使用默认角色。
    """

    if group_id:

        return get_group_character(
            group_id
        )


    from .character_binding import (
        DEFAULT_CHARACTER_ID
    )

    return DEFAULT_CHARACTER_ID