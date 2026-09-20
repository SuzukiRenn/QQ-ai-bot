import yaml



def validate_relationship(path):

    errors=[]


    with open(
        path,
        "r",
        encoding="utf-8"
    ) as f:

        data = yaml.safe_load(f)



    if "relationships" not in data:

        errors.append(
            "missing relationships"
        )

        return errors



    if "characters" not in data["relationships"]:

        errors.append(
            "missing relationships.characters"
        )


    return errors