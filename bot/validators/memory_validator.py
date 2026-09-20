import os
import yaml



REQUIRED_MEMORY_FIELDS = [
    "id",
    "title",
    "description",
    "tags",
    "emotional_impact",
    "importance",
]



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



def validate_memory_file(path):

    print(
        f"\nChecking: {path}"
    )


    with open(
        path,
        "r",
        encoding="utf-8"
    ) as f:

        data = yaml.safe_load(f)


    errors = []


    if not data:

        errors.append(
            "File is empty"
        )

        return errors



    if "memories" not in data:

        errors.append(
            "Missing root key: memories"
        )

        return errors



    memories = data["memories"]


    if not isinstance(
        memories,
        list
    ):

        errors.append(
            "memories must be a list"
        )

        return errors



    for index, memory in enumerate(memories):

        prefix = f"memory[{index}]"


        for field in REQUIRED_MEMORY_FIELDS:

            if field not in memory:

                errors.append(
                    f"{prefix}: missing {field}"
                )



        if "emotional_impact" in memory:

            if not isinstance(
                memory["emotional_impact"],
                dict
            ):

                errors.append(
                    f"{prefix}: emotional_impact must be dict"
                )



        if "tags" in memory:

            if not isinstance(
                memory["tags"],
                list
            ):

                errors.append(
                    f"{prefix}: tags must be list"
                )


    return errors





def validate_all_characters():


    for character in os.listdir(
        CHARACTER_DIR
    ):


        path = os.path.join(
            CHARACTER_DIR,
            character,
            "memories.yaml"
        )


        if not os.path.exists(path):

            print(
                f"{character}: missing memories.yaml"
            )

            continue



        errors = validate_memory_file(
            path
        )



        if errors:

            print(
                f"\n❌ {character} FAILED"
            )


            for error in errors:

                print(
                    " -",
                    error
                )


        else:

            print(
                f"✅ {character} OK"
            )




if __name__ == "__main__":

    validate_all_characters()