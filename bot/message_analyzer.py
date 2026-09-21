import json

from .llm import client
from .conversation_formatter import (
    format_conversation_messages
)


# ============================================================
# Character Name Helpers
# ============================================================

def build_character_names(
    character_name=None,
    character_aliases=None
):
    """
    整理当前角色所有可用于识别的名字。

    包括：

    - 正式名字
    - aliases

    返回去重后的字符串列表。
    """

    names = []


    if character_name:

        name = str(
            character_name
        ).strip()

        if name:

            names.append(
                name
            )


    for alias in (
        character_aliases
        or []
    ):

        if alias is None:

            continue


        alias = str(
            alias
        ).strip()


        if (
            alias
            and alias not in names
        ):

            names.append(
                alias
            )


    return names


def has_explicit_character_name(
    message,
    character_names
):
    """
    判断消息中是否明确出现当前角色名字 / 别名。

    这是确定性证据，
    优先级高于 LLM target 判断。
    """

    normalized_message = (
        str(message)
        .strip()
        .lower()
    )


    if not normalized_message:

        return False


    for name in character_names:

        normalized_name = (
            str(name)
            .strip()
            .lower()
        )


        if not normalized_name:

            continue


        if (
            normalized_name
            in normalized_message
        ):

            return True


    return False


def is_direct_followup(
    recent_messages,
    current_user_id,
    character_id,
    max_gap_seconds=120
):
    """
    判断是否属于：

    用户A
      ↓
    角色回复A
      ↓
    用户A继续接话

    这种连续对话属于明确 Reactive 对话。
    """

    messages = list(
        recent_messages
        or []
    )


    if len(messages) < 3:

        return False


    current = messages[-1]

    character_message = messages[-2]

    previous_user_message = messages[-3]


    # 当前消息必须是这个用户刚发的

    if str(
        current.get(
            "user_id"
        )
    ) != str(
        current_user_id
    ):

        return False


    if current.get(
        "sender_type",
        "user"
    ) != "user":

        return False


    # 上一句必须是当前角色说的

    if character_message.get(
        "sender_type"
    ) != "character":

        return False


    if (
        character_id
        and str(
            character_message.get(
                "user_id"
            )
        ) != str(
            character_id
        )
    ):

        return False


    # 角色上一句话之前，
    # 必须也是当前这个用户在和角色交流

    if previous_user_message.get(
        "sender_type",
        "user"
    ) != "user":

        return False


    if str(
        previous_user_message.get(
            "user_id"
        )
    ) != str(
        current_user_id
    ):

        return False


    # 时间不能隔得过久

    try:

        gap = (
            float(
                current.get(
                    "time",
                    0
                )
            )
            -
            float(
                character_message.get(
                    "time",
                    0
                )
            )
        )

    except (
        TypeError,
        ValueError
    ):

        return False


    if gap < 0:

        return False


    return (
        gap
        <= max_gap_seconds
    )


# ============================================================
# Main Analyzer
# ============================================================

def analyze_message(
    message,
    character_name=None,
    character_aliases=None,
    chat_type="private",
    recent_messages=None,
    current_user_id=None,
    character_id=None
):

    character_aliases = (
        character_aliases
        or []
    )


    recent_messages = (
        recent_messages
        or []
    )


    direct_followup = is_direct_followup(

        recent_messages=
            recent_messages,

        current_user_id=
            current_user_id,

        character_id=
            character_id

    )


    character_names = build_character_names(

        character_name=character_name,

        character_aliases=character_aliases

    )


    explicit_character_name = (
        has_explicit_character_name(

            message=message,

            character_names=
                character_names

        )
    )


    aliases_text = (

        "、".join(
            str(alias)
            for alias in character_aliases
        )

        if character_aliases

        else "无"

    )

    recent_chat_text = (
        format_conversation_messages(
            recent_messages,
            limit=8
        )
        if recent_messages
        else "无"
    )


    # ========================================================
    # Prompt
    # ========================================================

    prompt = f"""
你是一个聊天消息理解器。

你的任务：

分析一条聊天消息的语义，
判断这句话是否是在直接和当前角色说话。

不要生成回复。


====================
当前角色
====================

正式名字：

{character_name}


角色别名：

{aliases_text}


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
最近对话
====================

{recent_chat_text}


====================
连续对话提示
====================

当前消息是否满足：

同一用户 → 角色回复 → 同一用户继续接话

{direct_followup}


如果 direct_followup = True：

说明当前用户正在自然延续与角色的上一轮对话。

即使当前消息：

- 没再次叫角色名字
- 没出现“你”
- 只是纠正、吐槽、反驳或补充上一句话

通常也应该判断：

target = character


例如：

用户：
“黑猫黑猫黑猫”

角色：
“喵！别一直叫啦……虽然现在只是在晒太阳。”

同一用户：
“现在是晚上哪有太阳”

最后一句应该：

target = character


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
角色名字规则
====================

当前角色可能拥有：

正式名字
+
角色别名


只要消息明确使用当前角色的正式名字
或者角色别名呼叫、评价、询问当前角色，

应该判断：

target = character


例如：

如果当前角色叫“黑猫”：

“黑猫晚上好”

target:
character


“黑猫是笨蛋”

target:
character


“黑猫你怎么看？”

target:
character


即使消息不是问句，

只要明显是在对当前角色进行评价、
吐槽、呼叫或者互动，

仍然应该判断：

target = character


例如：

“黑猫好笨”

不是普通广播消息，

而是在直接评价黑猫，

因此：

target = character


====================
群聊规则
====================

如果 chat_type = "group"：

必须有明确证据，
才能判断：

target = "character"


明确证据包括：

1. 直接叫当前角色正式名字

2. 直接叫当前角色别名

3. 明确 @ 当前角色

4. 明确使用“你”向当前角色提问，
并且上下文可以确定“你”就是当前角色

5. 明确询问角色本人

6. 明确要求角色做某件事

7. 明确评价、调侃、吐槽当前角色本人


例如：

“{character_name}，你今天干嘛？”

target:
character


“{character_name}是笨蛋”

target:
character


“{character_name}晚上好”

target:
character


“@{character_name} 你看看这个”

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

“王强说他也来，刚好差一个人。”

应该：

target:
third_person

person:
王强


“他俩昨天打得也太搞笑了哈哈哈哈。”

应该：

target:
unknown


“今天好累。”

如果是在群聊中，
没有明确对当前角色说：

target:
unknown


“今晚有没有人打游戏？”

如果没有明确叫当前角色：

target:
unknown


“这个游戏也太难了。”

target:
unknown


====================
讨论第三方人物
====================

例如：

“李兆基今天去打游戏吗？”

如果是在群聊中，
没有明确向当前角色提问：

target:
third_person

person:
李兆基


“李兆基昨天那波直接冲进去送了哈哈。”

target:
third_person

person:
李兆基


但是：

“你觉得李兆基昨天那波怎么样？”

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


例如：

“今天好累”

通常应该：

target:
character


“你觉得李兆基怎么样？”

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

如果没有任何证据表明用户在对角色说话，

优先：

target = "unknown"

而不是：

target = "character"


但是：

如果消息明确出现了当前角色名字或别名，
并且是在呼叫、评价、询问或吐槽角色，

应优先：

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


    # ========================================================
    # Default Result
    # ========================================================

    result = {

        "target": "unknown",

        "person": "",

        "intent": "chatting",

        "confidence": 0

    }


    # ========================================================
    # LLM Analyze
    # ========================================================

    try:

        response = (
            client
            .chat
            .completions
            .create(

                model="deepseek-chat",

                messages=[

                    {
                        "role":
                            "system",

                        "content":
                            "你负责理解聊天消息。"
                            "在群聊中必须严格区分"
                            "直接对角色说话和普通群聊。"
                    },

                    {
                        "role":
                            "user",

                        "content":
                            prompt
                    }

                ]

            )
        )


        content = (
            response
            .choices[0]
            .message
            .content
            .strip()
        )


        # ====================================================
        # 清理 Markdown JSON
        # ====================================================

        if content.startswith(
            "```"
        ):

            lines = (
                content
                .splitlines()
            )


            if lines:

                lines = (
                    lines[1:]
                )


            if (
                lines
                and
                lines[-1].strip()
                == "```"
            ):

                lines = (
                    lines[:-1]
                )


            content = (
                "\n".join(
                    lines
                )
                .strip()
            )


        # ====================================================
        # 截取 JSON
        # ====================================================

        start = (
            content.find(
                "{"
            )
        )

        end = (
            content.rfind(
                "}"
            )
        )


        if (
            start != -1
            and
            end != -1
            and
            end >= start
        ):

            content = (
                content[
                    start:end + 1
                ]
            )


        # ====================================================
        # JSON Parse
        # ====================================================

        try:

            parsed = (
                json.loads(
                    content
                )
            )


            if isinstance(
                parsed,
                dict
            ):

                result = parsed


        except Exception as e:

            print(
                "Message Analyzer JSON Error:",
                e
            )

            print(
                "Raw Message Analyzer Result:",
                content
            )


    except Exception as e:

        # LLM临时失败时，
        # 不应该让整个 Character Engine 崩掉。
        #
        # 后面仍然可以使用：
        #
        # 名字 / alias 确定性规则。

        print(
            "Message Analyzer LLM Error:",
            repr(e)
        )


    # ========================================================
    # Normalize Fields
    # ========================================================

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


    target = (
        result.get(
            "target",
            "unknown"
        )
    )


    if target not in valid_targets:

        target = "unknown"


    intent = (
        result.get(
            "intent",
            "chatting"
        )
    )


    if intent not in valid_intents:

        intent = "chatting"


    person = (
        result.get(
            "person",
            ""
        )
    )


    if person is None:

        person = ""


    person = str(
        person
    ).strip()


    try:

        confidence = float(

            result.get(
                "confidence",
                0
            )

        )


    except (
        TypeError,
        ValueError
    ):

        confidence = 0


    confidence = max(

        0.0,

        min(
            confidence,
            1.0
        )

    )


    # ========================================================
    # Deterministic Target Override
    # ========================================================
    #
    # 这是非常重要的一层。
    #
    # LLM 负责理解模糊语义，
    # 但明确名字 / alias 属于确定性证据。
    #
    # 如果群聊消息明确包含：
    #
    # 黑猫
    # 丛雨
    # 从雨
    # ...
    #
    # 则不能因为 LLM 偶尔判断 unknown
    # 就导致角色完全不回应。
    # ========================================================

    if chat_type == "group":

      # 明确叫名字 / aliases
      if explicit_character_name:

          target = "character"
          confidence = 1.0


      # 用户 → 角色 → 同一用户继续对话
      elif direct_followup:

          target = "character"

          confidence = max(
              confidence,
              0.95
          )


    # ========================================================
    # Private Chat Safety
    # ========================================================
    #
    # 私聊默认就是用户在和角色交流。
    #
    # 如果 LLM 给了 unknown，
    # 这里做一次保守修正。
    # ========================================================

    if (
        chat_type == "private"
        and
        target == "unknown"
    ):

        target = (
            "character"
        )


        confidence = max(

            confidence,

            0.8

        )


    # ========================================================
    # Final Result
    # ========================================================

    return {

        "target":
            target,

        "person":
            person,

        "intent":
            intent,

        "confidence":
            confidence

    }