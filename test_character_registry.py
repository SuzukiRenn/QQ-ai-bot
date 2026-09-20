from bot.character_registry import (
    get_valid_characters
)


if __name__ == "__main__":


    characters = get_valid_characters()


    print()

    print(
        "可用角色:"
    )


    for c in characters:

        print(
            "-",
            c
        )