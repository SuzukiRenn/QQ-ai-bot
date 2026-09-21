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


# ============================================================
# Explicit Character Name
# ============================================================

def has_explicit_character_name(
    message,
    character_names
):
    """
    判断消息中是否明确出现当前角色名字 / 别名。

    这是确定性证据，
    优先级高于 LLM target 判断。

    例如：

    黑猫晚上好
    黑猫是笨蛋
    小黑猫你怎么看
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


# ============================================================
# Direct Follow-up
# ============================================================

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

    注意：

    这里只表示“存在连续对话结构”。

    最终是否仍然是在和角色说话，
    还要检查当前消息是否明确切换到了第三方对象。

    因此 direct_followup 不是最高优先级规则。
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


    # ========================================================
    # 当前消息必须来自当前用户
    # ========================================================

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


    # ========================================================
    # 上一句必须是当前角色发送
    # ========================================================

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


    # ========================================================
    # 角色上一句话之前，
    # 必须也是当前用户
    # ========================================================

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


    # ========================================================
    # 时间间隔限制
    # ========================================================

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
# Explicit Third-Person Addressee
# ============================================================

def is_explicit_third_person_addressee(
    message,
    person,
    character_names
):
    """
    判断当前消息是否明确把第三方作为说话对象。

    例如：

    高晋勋，来玩原神
    李兆基 你来一下
    王强，你在吗？
    小明：过来帮忙

    这种情况下：

    即使上一轮正在和角色聊天，
    当前 target 也必须切换为 third_person。

    注意：

    “你觉得李兆基怎么样？”

    中的李兆基只是讨论对象，
    并不是说话对象，
    因为名字不在句首直接呼叫位置。
    """

    if not person:

        return False


    normalized_message = (
        str(message)
        .strip()
        .lower()
    )


    normalized_person = (
        str(person)
        .strip()
        .lower()
    )


    if not normalized_person:

        return False


    # ========================================================
    # person 如果其实就是当前角色名字 / alias
    # 则不能当第三方
    # ========================================================

    for name in character_names:

        normalized_name = (
            str(name)
            .strip()
            .lower()
        )


        if (
            normalized_name
            and normalized_name
            == normalized_person
        ):

            return False


    # ========================================================
    # 必须明确以第三方名字开头
    # ========================================================

    if not normalized_message.startswith(
        normalized_person
    ):

        return False


    remaining = normalized_message[
        len(normalized_person):
    ]


    # ========================================================
    # 单独一个名字
    #
    # 例如：
    #
    # 高晋勋
    #
    # 也可以视为明确呼叫第三方。
    # ========================================================

    if not remaining:

        return True


    # 去除名字后的前导空白

    remaining = (
        remaining.lstrip()
    )


    if not remaining:

        return True


    # ========================================================
    # 明确呼叫模式
    # ========================================================
    #
    # 高晋勋，来玩原神
    # 高晋勋, 来一下
    # 高晋勋：过来
    # 高晋勋！你在哪
    # 高晋勋？在吗
    # 高晋勋你过来
    # ========================================================

    if remaining.startswith(
        (
            "，",
            ",",
            "：",
            ":",
            "！",
            "!",
            "？",
            "?",
            "你"
        )
    ):

        return True


    return False


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


    # ========================================================
    # Character Names
    # ========================================================

    character_names = build_character_names(

        character_name=
            character_name,

        character_aliases=
            character_aliases

    )


    explicit_character_name = (
        has_explicit_character_name(

            message=
                message,

            character_names=
                character_names

        )
    )


    # ========================================================
    # Conversation Follow-up
    # ========================================================

    direct_followup = (
        is_direct_followup(

            recent_messages=
                recent_messages,

            current_user_id=
                current_user_id,

            character_id=
                character_id

        )
    )


    # ========================================================
    # Prompt Context
    # ========================================================

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
判断这句话当前主要是在对谁说。

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
当前用户消息
====================

{message}


====================
最近对话
====================

{recent_chat_text}


====================
连续对话结构
====================

当前消息是否满足：

同一用户
→ 当前角色回复
→ 同一用户继续发言

结果：

{direct_followup}


注意：

direct_followup 只表示：

“当前消息可能是在延续与角色的上一轮对话”。

它不是绝对规则。


如果当前消息明确出现新的说话对象：

例如：

用户：
“你笨”

角色：
“你才笨呢！”

同一用户：
“高晋勋，来玩原神”

虽然形式上是：

用户
→ 角色
→ 同一用户

但是当前消息已经明确转向：

高晋勋

因此：

target = third_person


再例如：

角色：
“我刚才在晒太阳。”

同一用户：
“现在是晚上哪有太阳”

当前消息没有出现新的说话对象，
而且语义明显是在纠正角色上一句话。

因此：

target = character


核心原则：

明确说话对象
优先于
连续对话结构。


====================
需要判断
====================

1. target


target 表示：

“当前这句话主要是在对谁说”

而不是：

“这句话里面提到了谁”。


target 只能是：

character
user
third_person
unknown


--------------------
character
--------------------

消息明确是在与当前角色交流。


例如：

“黑猫晚上好”

“黑猫是笨蛋”

“你刚才不是这么说的吧？”

如果最后一句明显是在延续角色上一句话，
也可以是：

character


--------------------
user
--------------------

消息主要是在描述当前用户自己，

且没有明显向角色或第三方发起交流。


--------------------
third_person
--------------------

消息明确在对第三方说话，

或者主要围绕第三方人物进行直接交流。


尤其注意：

名字出现在句首并形成呼叫结构时，
通常意味着这个名字对应的人是当前说话对象。


例如：

“高晋勋，来玩原神”

target:
third_person

person:
高晋勋


“王强，你过来一下”

target:
third_person

person:
王强


--------------------
unknown
--------------------

普通群聊、
广播式发言、
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

如果消息涉及明确第三方人物，

提取名字。

没有则返回空字符串。


注意：

person 表示：

“消息中提到或涉及的人”

而 target 表示：

“当前这句话主要是在对谁说”。


二者不能混淆。


====================
最高优先级：当前角色名字
====================

如果消息明确使用当前角色：

正式名字
或
角色别名

进行：

- 呼叫
- 提问
- 评价
- 调侃
- 吐槽
- 指令
- 互动

应该：

target = character


例如当前角色是黑猫：

“黑猫晚上好”

target:
character


“黑猫是笨蛋”

target:
character


“黑猫你怎么看？”

target:
character


即使不是问句：

“黑猫好笨”

也属于：

target = character


====================
第二优先级：明确第三方呼叫
====================

如果消息明确以第三方名字作为说话对象，

应该：

target = third_person


例如：

“高晋勋，来玩原神”

target:
third_person

person:
高晋勋


“李兆基，你今晚打游戏吗？”

target:
third_person

person:
李兆基


“王强你过来一下”

target:
third_person

person:
王强


即使上一句话是当前角色回复的，

只要当前用户明确转向新的第三方对象，

也必须认为对话对象已经切换。


====================
讨论第三方 ≠ 对第三方说话
====================

例如：

“你觉得李兆基怎么样？”

如果“你”明确指当前角色：

target:
character

person:
李兆基


这里：

李兆基只是被讨论的人，

不是被直接呼叫的人。


====================
连续对话规则
====================

只有在：

1. 当前消息没有明确叫当前角色名字之外的新对象
2. 当前消息没有明确呼叫第三方
3. 上一句确实是当前角色对这个用户的回复
4. 时间间隔合理
5. 当前语义能够自然承接角色上一句话

时，

direct_followup 才应该支持：

target = character


例如：

角色：
“今天太阳很好。”

用户：
“现在明明是晚上。”

target:
character


角色：
“你才笨呢。”

用户：
“才没有。”

target:
character


但是：

角色：
“你才笨呢。”

用户：
“高晋勋，来玩原神。”

target:
third_person


====================
群聊普通消息
====================

如果 chat_type = "group"：

不要因为一句话：

- 是一个问题
- 角色可以回答
- 角色知道相关内容
- 角色对此感兴趣
- 角色可以自然接话

就判断：

target = character


例如：

“今晚有没有人打游戏？”

如果没有明确角色对象：

target:
unknown


“今天好热。”

target:
unknown


“他俩昨天也太搞笑了哈哈哈。”

target:
unknown


====================
私聊规则
====================

如果 chat_type = "private"：

用户默认是在与当前角色交流。


例如：

“今天好累”

通常：

target:
character


“你觉得李兆基怎么样？”

target:
character

person:
李兆基


只有非常明确的：

引用、
转述、
向第三方说话

才应该改变 target。


====================
最终判断原则
====================

群聊 Target 优先级：

1. 明确叫当前角色正式名字 / alias

2. 明确叫第三方人物

3. 明确的连续角色对话

4. 其他语义由上下文判断

5. 完全不确定时使用 unknown


绝对不要：

因为刚才用户在和角色聊天，

就认为这个用户接下来的每一句话都仍然是对角色说的。


群聊中人物可以随时切换交流对象。


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

        "target":
            "unknown",

        "person":
            "",

        "intent":
            "chatting",

        "confidence":
            0

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

                model=
                    "deepseek-chat",

                messages=[

                    {
                        "role":
                            "system",

                        "content":
                            "你负责理解聊天消息。"
                            "必须判断当前消息真正的说话对象。"
                            "群聊中允许用户随时从角色转向第三方。"
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

        # LLM 失败时，
        # 后面的确定性规则仍然可以工作。

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

        target = (
            "unknown"
        )


    intent = (
        result.get(
            "intent",
            "chatting"
        )
    )


    if intent not in valid_intents:

        intent = (
            "chatting"
        )


    person = (
        result.get(
            "person",
            ""
        )
    )


    if person is None:

        person = ""


    person = (
        str(
            person
        )
        .strip()
    )


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
    # Explicit Third Person
    # ========================================================

    explicit_third_person = (
        is_explicit_third_person_addressee(

            message=
                message,

            person=
                person,

            character_names=
                character_names

        )
    )


    # ========================================================
    # Deterministic Target Resolution
    # ========================================================
    #
    # 最终优先级：
    #
    # 1. 明确叫当前角色
    #
    # 2. 明确叫第三方
    #
    # 3. 连续对话
    #
    # 4. 保留 LLM 判断
    #
    # 这是修复：
    #
    # 黑猫：你才笨！
    # 用户：高晋勋，来玩原神
    #
    # 被错误识别成继续和黑猫说话的问题。
    # ========================================================

    if chat_type == "group":

        # ====================================================
        # 1. 明确叫当前角色
        # ====================================================

        if explicit_character_name:

            target = (
                "character"
            )


            confidence = (
                1.0
            )


        # ====================================================
        # 2. 明确叫第三方
        # ====================================================

        elif explicit_third_person:

            target = (
                "third_person"
            )


            confidence = max(

                confidence,

                0.95

            )


        # ====================================================
        # 3. 连续对话
        # ====================================================
        #
        # direct_followup 只能在：
        #
        # 没有明确切换到第三方
        #
        # 的情况下生效。
        #
        # 如果 LLM 已经非常明确判断 third_person，
        # 也不要用 direct_followup 覆盖。
        # ====================================================

        elif direct_followup:

            if target != "third_person":

                target = (
                    "character"
                )


                confidence = max(

                    confidence,

                    0.95

                )


    # ========================================================
    # Private Chat Safety
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
    # Debug Info
    # ========================================================
    #
    # 这几项只用于当前调试阶段。
    #
    # 等 target 系统稳定后，
    # 如果觉得日志太多可以删除。
    # ========================================================

    print(
        "Target Signals:",
        {
            "explicit_character":
                explicit_character_name,

            "explicit_third_person":
                explicit_third_person,

            "direct_followup":
                direct_followup,

            "llm_target":
                result.get(
                    "target",
                    "unknown"
                ),

            "final_target":
                target
        }
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