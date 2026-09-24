import os
import sys


from .card_validator import (
    validate_card
)

from .lore_validator import (
    validate_lore
)

from .memory_validator import (
    validate_memory_file
)

from .relationship_validator import (
    validate_relationship
)

from .event_validator import (
    validate_events
)

from .behavior_validator import (
    validate_behavior
)

from .dialogue_validator import (
    validate_dialogue_style
)



BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)


CHARACTER_DIR = os.path.join(
    BASE_DIR,
    "bot",
    "characters"
)



FILES = {


    "card.yaml":

    validate_card,


    "lore.yaml":

    validate_lore,


    "memories.yaml":

    validate_memory_file,


    "relationships.yaml":

    validate_relationship,


    "events.yaml":

    validate_events,


    "reply_behavior.yaml":

    validate_behavior

}


OPTIONAL_FILES = {

    "dialogue_examples.yaml":

    validate_dialogue_style

}


def validate_character_package(
    character_id
):


    print()

    print(
        "=" * 50
    )

    print(
        f"Character Package: {character_id}"
    )

    print(
        "=" * 50
    )



    character_path = os.path.join(
        CHARACTER_DIR,
        character_id
    )


    if not os.path.exists(
        character_path
    ):

        print(
            "❌ Character not found"
        )

        return False



    success = True



    for filename, validator in FILES.items():


        path = os.path.join(
            character_path,
            filename
        )


        if not os.path.exists(path):

            print(
                f"❌ {filename} missing"
            )

            success = False

            continue



        errors = validator(
            path
        )



        if errors:

            print(
                f"❌ {filename}"
            )


            for error in errors:

                print(
                    "   -",
                    error
                )


            success = False



        else:

            print(
                f"✅ {filename}"
            )



    # Dialogue Style System v1 是可选扩展。
    # 没有该文件的旧角色包仍保持 v1.1 兼容；存在时则进行校验。
    for filename, validator in OPTIONAL_FILES.items():

        path = os.path.join(
            character_path,
            filename
        )

        if not os.path.exists(path):
            continue

        errors = validator(path)

        if errors:
            print(f"❌ {filename}")
            for error in errors:
                print("   -", error)
            success = False
        else:
            print(f"✅ {filename} (optional)")


    print()


    if success:

        print(
            "🎉 Character Package Valid"
        )

    else:

        print(
            "⚠ Character Package Invalid"
        )


    return success





if __name__ == "__main__":


    if len(sys.argv) < 2:

        print(
            "Usage:"
        )

        print(
            "python -m bot.validators.package_validator character_id"
        )

        sys.exit(1)



    validate_character_package(
        sys.argv[1]
    )