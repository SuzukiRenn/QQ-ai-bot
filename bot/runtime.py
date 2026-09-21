from .character_manager import CharacterManager


character_manager = CharacterManager()


def init_runtime():

    character_manager.load_all_characters()


    print(
        "Character runtime initialized:"
    )


    print(
        character_manager.list_loaded()
    )