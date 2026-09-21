from bot.character_loader import (
    load_character_package
)



def test(character_id):


    character = load_character_package(
        character_id
    )


    print()

    print(
        "=" * 40
    )

    print(
        "角色:",
        character_id
    )

    print(
        "=" * 40
    )


    print(
        "模块:"
    )


    for key in character.keys():

        print(
            "-",
            key
        )



    print()


    print(
        "名字:",
        character["character"]["meta"]["name"]
    )


    print(
        "行为模块:",
        character["reply_behavior"].keys()
    )





if __name__ == "__main__":


    test(
        "black_cat"
    )


    test(
        "maomao"
    )