def build_prompt(character):

    prompt = f"""
你的名字：
{character['name']}

你的身份：
{character['identity']}

你的性格：
{', '.join(character['personality'])}

你的说话方式：
{', '.join(character['speaking_style'])}

你的喜好：
{', '.join(character['likes'])}

你的规则：
{', '.join(character['rules'])}
"""

    return prompt
