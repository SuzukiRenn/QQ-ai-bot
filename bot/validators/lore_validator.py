import yaml



REQUIRED = [

    "world",

    "rules",

    "locations",

    "culture"

]



def validate_lore(path):

    errors=[]


    with open(
        path,
        "r",
        encoding="utf-8"
    ) as f:

        data = yaml.safe_load(f)



    for key in REQUIRED:

        if key not in data:

            errors.append(
                f"missing: {key}"
            )


    return errors