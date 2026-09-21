from bot.emotion_context import (
    build_emotion_context
)



def test(
    character_id,
    user_id
):

    context = build_emotion_context(
        character_id,
        user_id
    )


    print(
        "\n",
        character_id
    )

    print(context)



if __name__ == "__main__":


    test(
        "black_cat",
        "001"
    )


    test(
        "maomao",
        "001"
    )