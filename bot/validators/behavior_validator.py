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

        proactive = behavior.get(
        "proactive"
    )


        if proactive is not None:

            errors.extend(
                validate_proactive(
                    proactive
                )
            )


    return errors


def validate_proactive(
    proactive
):

    errors = []


    if not isinstance(
        proactive,
        dict
    ):

        return [
            "reply_behavior.proactive must be a mapping"
        ]


    # enabled

    if "enabled" in proactive:

        if not isinstance(
            proactive["enabled"],
            bool
        ):

            errors.append(
                "reply_behavior.proactive.enabled "
                "must be boolean"
            )


    # min_context_messages

    if "min_context_messages" in proactive:

        value = proactive[
            "min_context_messages"
        ]

        if (
            not isinstance(
                value,
                int
            )
            or isinstance(
                value,
                bool
            )
            or value < 1
        ):

            errors.append(
                "reply_behavior.proactive."
                "min_context_messages "
                "must be integer >= 1"
            )


    # min_join_probability

    if "min_join_probability" in proactive:

        value = proactive[
            "min_join_probability"
        ]

        if (
            isinstance(
                value,
                bool
            )
            or not isinstance(
                value,
                (int, float)
            )
            or value < 0
            or value > 1
        ):

            errors.append(
                "reply_behavior.proactive."
                "min_join_probability "
                "must be between 0 and 1"
            )


    # cooldown_seconds

    if "cooldown_seconds" in proactive:

        value = proactive[
            "cooldown_seconds"
        ]

        if (
            not isinstance(
                value,
                int
            )
            or isinstance(
                value,
                bool
            )
            or value < 0
        ):

            errors.append(
                "reply_behavior.proactive."
                "cooldown_seconds "
                "must be integer >= 0"
            )


    return errors