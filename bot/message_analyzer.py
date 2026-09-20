import json

from llm import client



def analyze_message(
    message,
    character_name=None
):

    prompt = f"""

你是一个聊天消息理解器。

分析用户消息，不生成回复。

当前角色：

{character_name}


用户消息：

{message}


请判断：

1. 用户在和谁说话？

target:

- character
  角色本人

- user
  当前用户自己

- third_person
  第三方人物

- unknown
  无法判断



2. 用户意图：

intent:

- asking
  提问

- chatting
  普通聊天

- mentioning
  提到某人某事

- command
  指令


3. 如果提到了人物：

提取名字。


返回 JSON：

{{
    "target":"",
    "person":"",
    "intent":"",
    "confidence":0
}}


规则：

不要把出现的人名默认认为是角色本人。

例如：

"高勋今天去打球吗？"

应该判断为：

target:
third_person


"猫猫你今天怎么样？"

应该判断为：

target:
character


只返回JSON。
"""


    response = client.chat.completions.create(
        model="deepseek-chat",

        messages=[

            {
                "role":"system",
                "content":"你负责理解用户消息。"
            },

            {
                "role":"user",
                "content":prompt
            }

        ]
    )


    return json.loads(
        response.choices[0].message.content
    )