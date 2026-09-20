import os
import yaml


REQUIRED_TOP_LEVEL = [
    "reply_type_behavior",
    "relationship_behavior",
    "emotion_behavior",
    "scene_behavior",
]


def validate_reply_behavior(path):

    print(f"\nChecking: {path}")

    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)


    errors = []


    # 一级 reply_behavior
    if "reply_behavior" not in data:
        errors.append(
            "Missing root key: reply_behavior"
        )
        return errors


    behavior = data["reply_behavior"]


    # 检查四大模块
    for key in REQUIRED_TOP_LEVEL:

        if key not in behavior:
            errors.append(
                f"Missing section: {key}"
            )


    # 检查 description/rules

    for section_name, section in behavior.items():

        if not isinstance(section, dict):
            continue


        for item_name, item in section.items():

            if not isinstance(item, dict):
                continue


            if "description" not in item:
                errors.append(
                    f"{section_name}.{item_name}: missing description"
                )


            if "rules" not in item:
                errors.append(
                    f"{section_name}.{item_name}: missing rules"
                )


    return errors



def validate_all_characters():

    base = os.path.join(
        "bot",
        "characters"
    )

    for character in os.listdir(base):

        path = os.path.join(
            base,
            character,
            "reply_behavior.yaml"
        )


        if not os.path.exists(path):
            print(
                f"{character}: missing reply_behavior.yaml"
            )
            continue


        errors = validate_reply_behavior(path)


        if errors:

            print(
                f"\n❌ {character} FAILED"
            )

            for e in errors:
                print(
                    " -",
                    e
                )

        else:

            print(
                f"✅ {character} OK"
            )



if __name__ == "__main__":

    validate_all_characters()