from bot.knowledge import load_character_knowledge
from bot.character_manager import load_character

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


    prompt = build_prompt(
        character=character,
        knowledge=knowledge,
        relationship={
            "trust":70,
            "intimacy":70,
            "familiarity":70
        },
        relationship_level="friend",
        reply_type="tease"
    )


    print(prompt)



if __name__ == "__main__":


    test_character(
        "black_cat"
    )


    test_character(
        "maomao"
    )