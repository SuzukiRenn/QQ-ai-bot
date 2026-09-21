from bot.character_manager import (
    CharacterManager
)



if __name__ == "__main__":


    manager = CharacterManager()


    manager.load_all_characters()



    print()

    print(
        "已加载角色:"
    )


    for c in manager.list_loaded():

        print(
            "-",
            c
        )



    print()


    black_cat = manager.get(
        "black_cat"
    )


    print(
        "黑猫名字:",
        black_cat["character"]["meta"]["name"]
    )