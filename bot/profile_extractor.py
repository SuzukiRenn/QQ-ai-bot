import os
import json

from dotenv import load_dotenv
from .llm import client

load_dotenv()

def extract_profile(message):

    prompt = f"""
你是一个用户信息提取器。

从用户消息中提取长期有价值的信息。

只提取：

- 用户名字
- 兴趣爱好
- 习惯
- 喜欢的东西
- 讨厌的东西
- 重要背景


用户消息：

{message}


如果没有信息，返回空JSON。

返回格式：

{{
"name": null,
"likes": [],
"dislikes": [],
"notes": []
}}

只返回JSON，不要解释。
"""


    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {
                "role":"system",
                "content":"你负责提取用户资料。"
            },
            {
                "role":"user",
                "content":prompt
            }
        ]
    )


    content = response.choices[0].message.content


    return json.loads(content)