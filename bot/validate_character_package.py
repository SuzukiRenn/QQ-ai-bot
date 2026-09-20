import os
import sys


from .validate_character import (
    validate_reply_behavior
)

from .validate_memory import (
    validate_memory_file
)



BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)


CHARACTER_DIR = os.path.join(
    BASE_DIR,
    "bot",
    "characters"
)



REQUIRED_FILES = [

    "card.yaml",

    "lore.yaml",

    "memories.yaml",

    "relationships.yaml",

    "events.yaml",

    "reply_behavior.yaml"

]



def check_file_exists(
    character_path,
    filename
):

    path = os.path.join(
        character_path,
        filename
    )


    return os.path.exists(path)





def validate_lore(path):

    import yaml


    with open(
        path,
        "r",
        encoding="utf-8"
    ) as f:

        data = yaml.safe_load(f)


    required = [

        "world",

        "rules",

        "locations",

        "culture"

    ]


    errors = []


    for key in required:

        if key not in data:

            errors.append(
                f"missing {key}"
            )


    return errors





def validate_relationships(path):

    import yaml


    with open(
        path,
        "r",
        encoding="utf-8"
    ) as f:

        data = yaml.safe_load(f)


    errors = []


    if "relationships" not in data:

        errors.append(
            "missing relationships root"
        )

        return errors



    if "characters" not in data["relationships"]:

        errors.append(
            "missing characters"
        )


    return errors





def validate_events(path):

    import yaml


    with open(
        path,
        "r",
        encoding="utf-8"
    ) as f:

        data = yaml.safe_load(f)


    errors = []


    if "events" not in data:

        errors.append(
            "missing events root"
        )

        return errors



    if not isinstance(
        data["events"],
        list
    ):

        errors.append(
            "events must be list"
        )


    return errors





def validate_character_package(
    character_id
):


    print()

    print(
        "=" * 40
    )

    print(
        f"Character: {character_id}"
    )

    print(
        "=" * 40
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



    # 文件检查

    for filename in REQUIRED_FILES:


        if check_file_exists(
            character_path,
            filename
        ):

            print(
                f"✅ {filename}"
            )


        else:

            print(
                f"❌ missing {filename}"
            )

            success = False



    print()



    # Schema检查


    checks = {


        "lore.yaml":

        validate_lore(
            os.path.join(
                character_path,
                "lore.yaml"
            )
        ),



        "relationships.yaml":

        validate_relationships(
            os.path.join(
                character_path,
                "relationships.yaml"
            )
        ),



        "events.yaml":

        validate_events(
            os.path.join(
                character_path,
                "events.yaml"
            )
        )

    }



    for name, errors in checks.items():


        if errors:

            print(
                f"❌ {name}"
            )


            for error in errors:

                print(
                    "   -",
                    error
                )


            success = False


        else:

            print(
                f"✅ {name} schema"
            )



    print()



    if success:

        print(
            "🎉 Package Valid"
        )

    else:

        print(
            "⚠ Package Invalid"
        )



    return success





if __name__ == "__main__":


    if len(sys.argv) < 2:

        print(
            "Usage:"
        )

        print(
            "python -m bot.validate_character_package character_id"
        )

        sys.exit(1)



    validate_character_package(
        sys.argv[1]
    )