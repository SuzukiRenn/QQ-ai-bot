import yaml



def validate_events(path):

    errors=[]


    with open(
        path,
        "r",
        encoding="utf-8"
    ) as f:

        data = yaml.safe_load(f)



    if "events" not in data:

        errors.append(
            "missing events"
        )


    elif not isinstance(
        data["events"],
        list
    ):

        errors.append(
            "events must be list"
        )


    return errors