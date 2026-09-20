from bot.knowledge import load_character_knowledge
from bot.character_manager import load_character
from bot.emotion_context import build_emotion_context

from bot.prompt import build_prompt



def test_character(character_id):

    print("\n")
    print("=" * 50)
    print(
        "测试角色:",
        character_id
    )
    print("=" * 50)


    character = load_character(
        character_id
    )


    knowledge = load_character_knowledge(
        character_id
    )

    emotion_context = build_emotion_context(
        character_id,
        "001"
    )


    prompt = build_prompt(
        character=character,
        knowledge=knowledge,
        relationship={
            "trust":70,
            "intimacy":70,
            "familiarity":70
        },
        relationship_level="friend",
        reply_type="tease",
        emotion_context=emotion_context,
    )


    print(prompt)



if __name__ == "__main__":


    test_character(
        "black_cat"
    )


    test_character(
        "maomao"
    )