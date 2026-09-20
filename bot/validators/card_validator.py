import yaml



REQUIRED_PATHS = [

    "character",

    "character.meta",

    "character.identity",

    "character.personality",

    "character.speech_style",

    "character.behavior",

    "character.goals",

    "character.roleplay_rules"

]



def check_path(data, path):

    current = data


    for key in path.split("."):

        if key not in current:

            return False


        current = current[key]


    return True





def validate_card(path):

    errors = []


    with open(
        path,
        "r",
        encoding="utf-8"
    ) as f:

        data = yaml.safe_load(f)



    for required in REQUIRED_PATHS:

        if not check_path(
            data,
            required
        ):

            errors.append(
                f"missing: {required}"
            )


    return errors