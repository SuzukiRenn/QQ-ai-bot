import json

from .llm import client


def should_reply(
    message,
    relationship=None,
    emotion=None,
    message_context=None,
    chat_type="private"
):

    # =====================
    # 群聊 Reactive 硬规则
    # =====================
    #
    # 群聊里如果消息不是明确对角色说的，
    # Reactive 系统不参与。
    #
    # 后续交给 Proactive Behavior 判断
    # 角色是否主动加入聊天。
    # =====================

    if (
        chat_type == "group"
        and message_context
    ):

        target = message_context.get(
            "target",
            "unknown"
        )

        if target != "character":

            return {
                "should_reply": False,
                "reply_type": "ignore",
                "priority": 0,
                "reason": "group_message_not_directed_to_character"
            }


    # =====================
    # Reactive LLM Decision
    # =====================

    prompt = f"""

你是一个聊天角色回复决策器。

你的任务：

判断角色是否应该回复这条消息。

不要生成回复内容。


================
聊天类型
================

{chat_type}


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

只返回 JSON：

{{
    "should_reply": true,
    "reply_type": "",
    "priority": 0,
    "reason": ""
}}


================
reply_type 类型
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
基本原则
================

Reactive Reply 表示：

用户正在直接和角色交流，
所以角色需要决定如何回应。


如果 chat_type = "group"：

进入当前决策器的消息，
原则上应该已经是：

target = "character"

也就是说：

用户明确在和当前角色说话。


例如：

“黑猫，你今晚想不想打游戏？”

可以回复。


“你觉得李兆基这个人怎么样？”

如果消息理解结果表明：

target = character

说明用户是在询问角色观点，

可以回复。


================
私聊规则
================

如果 chat_type = "private"：

用户默认是在与角色交流。

例如：

“今天好累”

可以根据语义判断：

reply_type = comfort


“你今天干嘛？”

可以：

reply_type = answer


================
正常回复规则
================

应该回复的情况包括：

- 用户直接询问角色
- 用户明确叫角色名字
- 用户询问角色观点
- 用户需要角色帮助
- 用户表达情绪并明确与角色交流
- 用户给角色下达正常指令


reply_type：

问题：
answer

普通聊天：
chat

调侃：
tease

安慰：
comfort

分享：
share

打招呼：
greet


================
priority
================

100:
必须回复

50:
正常回复

0:
忽略


================
重要限制
================

不要因为：

- 角色心情很好
- 角色与用户关系很好
- 角色对这个话题感兴趣

就把普通群聊变成 Reactive Reply。

普通群聊是否主动加入，
由 Proactive Behavior 系统负责。


只返回 JSON。

不要解释。
不要使用 Markdown。
不要使用 ```json。
"""


    response = client.chat.completions.create(

        model="deepseek-chat",

        messages=[

            {
                "role": "system",
                "content":
                    "你负责判断直接面向角色的消息应该如何回复。"
            },

            {
                "role": "user",
                "content": prompt
            }

        ]

    )


    content = (
        response
        .choices[0]
        .message
        .content
        .strip()
    )


    # =====================
    # 清理 Markdown JSON
    # =====================

    if content.startswith("```"):

        lines = content.splitlines()

        if lines:
            lines = lines[1:]

        if (
            lines
            and lines[-1].strip() == "```"
        ):
            lines = lines[:-1]

        content = "\n".join(
            lines
        ).strip()


    # =====================
    # 截取 JSON
    # =====================

    start = content.find("{")
    end = content.rfind("}")

    if (
        start != -1
        and end != -1
    ):

        content = content[
            start:end + 1
        ]


    # =====================
    # JSON 解析
    # =====================

    try:

        result = json.loads(
            content
        )

    except Exception as e:

        print(
            "Reply Decision JSON Error:",
            e
        )

        print(
            "Raw Reply Decision Result:",
            content
        )

        return {
            "should_reply": False,
            "reply_type": "ignore",
            "priority": 0,
            "reason": "invalid_llm_result"
        }


    # =====================
    # 标准化结果
    # =====================

    valid_reply_types = {
        "answer",
        "chat",
        "tease",
        "comfort",
        "greet",
        "share",
        "ignore"
    }


    reply_type = result.get(
        "reply_type",
        "ignore"
    )

    if reply_type not in valid_reply_types:
        reply_type = "ignore"


    should_reply_value = result.get(
        "should_reply",
        False
    )


    if isinstance(
        should_reply_value,
        bool
    ):

        should_reply = should_reply_value

    else:

        should_reply = (
            str(
                should_reply_value
            ).lower()
            == "true"
        )


    try:

        priority = int(
            result.get(
                "priority",
                0
            )
        )

    except (TypeError, ValueError):

        priority = 0


    priority = max(
        0,
        min(
            priority,
            100
        )
    )


    return {
        "should_reply": should_reply,
        "reply_type": reply_type,
        "priority": priority,
        "reason": result.get(
            "reason",
            ""
        )
    }