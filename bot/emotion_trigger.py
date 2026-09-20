import json

from llm import client


def analyze_emotion_change(message):

    prompt = f"""
你是一个AI角色心理分析器。

分析用户的话对角色情绪产生的影响。

只输出JSON。


用户消息：

{message}


输出格式：

{{
  "emotion_change": {{
    "happiness": 0,
    "sadness": 0,
    "anger": 0,
    "trust": 0
  }},
  "reason": ""
}}


规则：

数值范围：
-100 到 100

正数:
增加

负数:
减少


判断：

安慰、关心:
增加 happiness/trust

赞美:
增加 happiness/trust

攻击、侮辱:
增加 anger

伤感话题:
增加 sadness


不要考虑角色回复，只分析用户行为影响。
"""


    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {
                "role":"system",
                "content":"你负责分析情绪变化。"
            },
            {
                "role":"user",
                "content":prompt
            }
        ]
    )


    content = response.choices[0].message.content


    return json.loads(content)