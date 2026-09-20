import yaml



REQUIRED_SECTIONS = [

    "reply_type_behavior",

    "relationship_behavior",

    "emotion_behavior",

    "scene_behavior"

]



def validate_behavior(path):

    errors = []


    with open(
        path,
        "r",
        encoding="utf-8"
    ) as f:

        data = yaml.safe_load(f)



    if "reply_behavior" not in data:

        return [
            "missing reply_behavior"
        ]


    behavior = data["reply_behavior"]


    for section in REQUIRED_SECTIONS:

        if section not in behavior:

            errors.append(
                f"missing: reply_behavior.{section}"
            )


    return errors