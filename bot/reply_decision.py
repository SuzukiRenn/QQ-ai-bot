import json

from .llm import client



def should_reply(
    message,
    relationship=None,
    emotion=None,
    message_context=None
):

    prompt = f"""

你是一个QQ群角色回复决策器。

你的任务：

判断角色是否应该回复这条消息。

不要生成回复内容。


================
用户消息
================

{message}



================
消息理解结果
================

{message_context}



================
角色与用户关系
================

{relationship}



================
当前情绪
================

{emotion}



================
返回格式
================

只返回JSON：

{{
    "should_reply": true,
    "reply_type": "",
    "priority": 0,
    "reason": ""
}}



================
reply_type类型
================

answer:
回答问题


chat:
普通聊天


tease:
调侃、开玩笑


comfort:
安慰用户


greet:
打招呼


share:
分享角色经历


ignore:
忽略，不回复



================
判断规则
================


第一优先级：

检查消息理解结果。


如果：

target = "third_person"


说明用户正在和第三方人物交流。


默认：

should_reply = false

reply_type = "ignore"



不要因为：

- 用户和角色关系很好
- 用户经常聊天
- 当前情绪积极

而回复第三方对话。


例如：

用户：
李兆基今天去打游戏吗？


判断：

不要回复。



但是：

用户：
你觉得李兆基这个人怎么样？


这是询问角色观点。

可以回复。



================
正常回复规则
================


应该回复：

- 用户直接询问角色
- 用户提到角色名字
- 用户询问角色观点
- 用户需要角色帮助
- 与角色相关的话题


回复类型：

问题:
answer


普通聊天:
chat


调侃:
tease


安慰:
comfort


分享:
share



priority:

100:
必须回复


50:
可以回复


0:
忽略



只返回JSON。
"""


    response = client.chat.completions.create(

        model="deepseek-chat",

        messages=[

            {
                "role":"system",
                "content":"你负责判断QQ群消息是否需要角色回复。"
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