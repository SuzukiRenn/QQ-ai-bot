import json
import os


RELATIONSHIP_FILE = "relationships.json"



def load_relationships():

    if not os.path.exists(
        RELATIONSHIP_FILE
    ):
        return {}


    with open(
        RELATIONSHIP_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)



def save_relationships(data):

    with open(
        RELATIONSHIP_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2
        )



def default_relationship():

    return {

        "trust": 0,

        "intimacy": 0,

        "familiarity": 0

    }



def get_relationship(
    character_id,
    user_id
):

    relationships = load_relationships()


    key = f"{character_id}:{user_id}"


    if key not in relationships:

        relationships[key] = default_relationship()


        save_relationships(
            relationships
        )


    return relationships[key]



def update_relationship(
    character_id,
    user_id,
    changes
):

    relationships = load_relationships()


    key = f"{character_id}:{user_id}"


    state = relationships.get(
        key,
        default_relationship()
    )


    for k, v in changes.items():

        # 只更新允许的关系字段
        if k in [
            "trust",
            "intimacy",
            "familiarity"
        ]:

            state[k] = max(
                0,
                min(
                    100,
                    state.get(k,0) + v
                )
            )


    relationships[key] = state


    save_relationships(
        relationships
    )


    return state



def get_relationship_level(
    state
):

    trust = state.get(
        "trust",
        0
    )

    intimacy = state.get(
        "intimacy",
        0
    )

    familiarity = state.get(
        "familiarity",
        0
    )


    # 综合评分
    score = (
        trust * 0.5
        +
        intimacy * 0.3
        +
        familiarity * 0.2
    )


    if score < 20:

        return "陌生人"


    elif score < 50:

        return "认识"


    elif score < 80:

        return "朋友"


    else:

        return "亲密朋友"