import os
import yaml



BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)


CHARACTER_DIR = os.path.join(
    BASE_DIR,
    "characters"
)





def load_yaml(path):

    if not os.path.exists(path):

        return {}


    with open(
        path,
        "r",
        encoding="utf-8"
    ) as f:

        data = yaml.safe_load(f)


    return data or {}





def load_character_package(
    character_id
):

    """
    加载完整角色包

    返回：

    {
        character:
        lore:
        memories:
        relationships:
        events:
        reply_behavior:
        dialogue_style:
    }

    """


    base = os.path.join(
        CHARACTER_DIR,
        character_id
    )


    if not os.path.exists(base):

        raise FileNotFoundError(
            f"Character not found: {character_id}"
        )



    package = {


        "character":

            load_yaml(
                os.path.join(
                    base,
                    "card.yaml"
                )
            )
            .get(
                "character",
                {}
            ),



        "lore":

            load_yaml(
                os.path.join(
                    base,
                    "lore.yaml"
                )
            ),



        "memories":

            load_yaml(
                os.path.join(
                    base,
                    "memories.yaml"
                )
            ),



        "relationships":

            load_yaml(
                os.path.join(
                    base,
                    "relationships.yaml"
                )
            ),



        "events":

            load_yaml(
                os.path.join(
                    base,
                    "events.yaml"
                )
            ),



        "reply_behavior":

            load_yaml(
                os.path.join(
                    base,
                    "reply_behavior.yaml"
                )
            )
            .get(
                "reply_behavior",
                {}
            ),


        # Dialogue Style System v1
        # 可选文件：旧角色包没有该文件时保持兼容。
        "dialogue_style":

            load_yaml(
                os.path.join(
                    base,
                    "dialogue_examples.yaml"
                )
            )
            .get(
                "dialogue_style",
                {}
            )

    }



    return package