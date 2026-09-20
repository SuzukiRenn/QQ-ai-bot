from bot.knowledge import load_character_knowledge

from bot.character_emotion import (
    generate_character_emotion,
    get_character_emotion
)



def test(character_id):

    knowledge = load_character_knowledge(
        character_id
    )


    emotion = generate_character_emotion(
        character_id,
        knowledge["memories"]
    )


    print(
        character_id,
        emotion
    )



if __name__ == "__main__":

    test(
        "black_cat"
    )

    test(
        "maomao"
    )


    print(
        get_character_emotion(
            "black_cat"
        )
    )