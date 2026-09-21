from bot.emotion_context import (
    build_emotion_context
)

from bot.emotion_formatter import (
    format_emotion_context
)



def test(character_id):

    context = build_emotion_context(
        character_id,
        "001"
    )


    text = format_emotion_context(
        context
    )


    print("\n")
    print("="*30)

    print(
        character_id
    )

    print(text)




if __name__ == "__main__":

    test(
        "black_cat"
    )


    test(
        "maomao"
    )