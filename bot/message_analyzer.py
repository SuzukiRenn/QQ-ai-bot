import json

from .llm import client


def analyze_message(
    message,
    character_name=None,
    chat_type="private"
):

    prompt = f"""
你是一个聊天消息理解器。

你的任务：

分析一条聊天消息的语义，
判断这句话是否是在直接和当前角色说话。

不要生成回复。


====================
当前角色
====================

{character_name}


====================
聊天类型
====================

{chat_type}


chat_type 可能是：

private
私聊

group
群聊


====================
用户消息
====================

{message}


====================
需要判断
====================

1. target

target 表示：

“这句话主要是在对谁说 / 是否明确需要当前角色回应”

而不是：

“这句话里面提到了谁”。


target 只能是：

character
user
third_person
unknown


character:

消息明确是在对当前角色说话。


user:

消息主要是在描述当前用户自己，
且没有明显向角色发起互动。


third_person:

消息主要围绕第三方人物，
同时没有明确向当前角色提问。


unknown:

普通群聊、广播式发言、
无法确定具体交流对象。


====================
2. intent
====================

intent 只能是：

asking
chatting
mentioning
command


====================
3. person
====================

如果消息涉及明确的第三方人物，
提取人物名字。

没有则返回空字符串。


====================
群聊规则
====================

如果 chat_type = "group"：

必须有明确证据，
才能判断：

target = "character"


明确证据包括：

1. 直接叫当前角色名字

例如：

"{character_name}，你今天干嘛？"

target:
character


2. 明确 @ 当前角色

例如：

"@{character_name} 你看看这个"

target:
character


3. 明确使用“你”向当前角色提问，
并且上下文可以确定“你”就是当前角色。

例如：

"你觉得这个游戏怎么样？"

如果明确是在和角色交流：

target:
character


4. 明确询问角色本人的事情。

例如：

"{character_name}喜欢玩什么游戏？"

target:
character


5. 明确要求角色做某件事情。

例如：

"{character_name}讲个笑话"

target:
character


====================
群聊中的普通聊天
====================

群聊中，

不要因为一句话：

- 是一个问题
- 看起来可以回答
- 角色可能知道答案
- 角色可能对此感兴趣
- 角色可以自然接话

就判断为 character。


例如：

"王强说他也来，刚好差一个人。"

应该：

target:
third_person

person:
王强


"他俩昨天打得也太搞笑了哈哈哈哈。"

应该：

target:
unknown


"今天好累。"

如果是在群聊中，
没有明确对当前角色说：

target:
unknown


"今晚有没有人打游戏？"

如果没有明确叫当前角色：

target:
unknown


"这个游戏也太难了。"

target:
unknown


====================
讨论第三方人物
====================

例如：

"李兆基今天去打游戏吗？"

如果是在群聊中，
没有明确向当前角色提问：

target:
third_person

person:
李兆基


"李兆基昨天那波直接冲进去送了哈哈。"

target:
third_person

person:
李兆基


但是：

"你觉得李兆基昨天那波怎么样？"

如果“你”明确指当前角色：

target:
character

person:
李兆基


注意：

person 表示消息里讨论的人。

target 表示消息是否在直接和角色交流。

两者不能混淆。


====================
私聊规则
====================

如果 chat_type = "private"：

默认用户是在和当前角色交流。

因此例如：

"今天好累"

通常应该：

target:
character


"你觉得李兆基怎么样？"

应该：

target:
character

person:
李兆基


不要仅仅因为提到了第三方人物，
就把私聊消息判断为 third_person。


====================
重要原则
====================

在群聊中：

如果不确定是不是在对角色说话，

优先：

target = "unknown"

而不是：

target = "character"


角色是否主动加入普通群聊，
由另一个 Proactive Behavior 系统决定。

你这里只负责判断：

“这条消息是不是明确在和角色说话？”


====================
返回格式
====================

只返回 JSON。

不要解释。

不要使用 Markdown。

不要使用 ```json。

格式：

{{
    "target": "",
    "person": "",
    "intent": "",
    "confidence": 0
}}
"""


    response = client.chat.completions.create(

        model="deepseek-chat",

        messages=[

            {
                "role": "system",
                "content":
                    "你负责理解聊天消息。"
                    "在群聊中必须严格区分直接对角色说话和普通群聊。"
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
            "Message Analyzer JSON Error:",
            e
        )

        print(
            "Raw Message Analyzer Result:",
            content
        )

        return {

            "target": "unknown",

            "person": "",

            "intent": "chatting",

            "confidence": 0

        }


    # =====================
    # 标准化字段
    # =====================

    valid_targets = {
        "character",
        "user",
        "third_person",
        "unknown"
    }


    valid_intents = {
        "asking",
        "chatting",
        "mentioning",
        "command"
    }


    target = result.get(
        "target",
        "unknown"
    )


    if target not in valid_targets:
        target = "unknown"


    intent = result.get(
        "intent",
        "chatting"
    )


    if intent not in valid_intents:
        intent = "chatting"


    try:

        confidence = float(
            result.get(
                "confidence",
                0
            )
        )

    except (TypeError, ValueError):

        confidence = 0


    confidence = max(
        0.0,
        min(
            confidence,
            1.0
        )
    )


    return {

        "target": target,

        "person": result.get(
            "person",
            ""
        ),

        "intent": intent,

        "confidence": confidence

    }