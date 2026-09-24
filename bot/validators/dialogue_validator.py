import yaml


def validate_dialogue_style(path):
    errors = []

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
    except Exception as e:
        return [f"YAML load failed: {e}"]

    style = data.get("dialogue_style", data)

    if not isinstance(style, dict):
        return ["dialogue_style must be a mapping"]

    anti_patterns = style.get("anti_patterns", [])
    if anti_patterns and not isinstance(anti_patterns, list):
        errors.append("dialogue_style.anti_patterns must be a list")

    examples = style.get("examples", [])
    if not isinstance(examples, list):
        errors.append("dialogue_style.examples must be a list")
        return errors

    seen_ids = set()

    for index, example in enumerate(examples):
        prefix = f"dialogue_style.examples[{index}]"

        if not isinstance(example, dict):
            errors.append(f"{prefix} must be a mapping")
            continue

        example_id = str(example.get("id", "")).strip()
        text = str(example.get("text", "")).strip()

        if not example_id:
            errors.append(f"{prefix}.id missing")
        elif example_id in seen_ids:
            errors.append(f"duplicate dialogue example id: {example_id}")
        else:
            seen_ids.add(example_id)

        if not text:
            errors.append(f"{prefix}.text missing")

        for field in (
            "reply_type",
            "emotion",
            "scene",
            "relationship",
            "keywords",
            "style_tags",
        ):
            value = example.get(field)
            if value is not None and not isinstance(value, (str, list)):
                errors.append(f"{prefix}.{field} must be string or list")

    return errors
