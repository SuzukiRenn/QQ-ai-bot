import json

from .llm import client



def analyze_relationship_change(
    message
):

    prompt = f"""

你是一个角色关系分析器。

分析用户这句话对角色关系的影响。


用户消息：

{message}


返回JSON：

{{
"relationship_change":{{

"trust":0,

"intimacy":0,

"familiarity":0

}},

"reason":""

}}


规则：

范围：

-100 到 100


正向：

关心
帮助
感谢
鼓励
分享秘密

增加：

trust
intimacy


普通聊天：

增加：

familiarity


负面：

侮辱
攻击
欺骗

降低：

trust


只返回JSON。
"""


    response = client.chat.completions.create(

        model="deepseek-chat",

        messages=[

            {
                "role":"system",
                "content":"你负责分析角色关系变化。"
            },

            {
                "role":"user",
                "content":prompt
            }

        ]

    )


    content = response.choices[0].message.content


    return json.loads(content)