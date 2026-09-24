from .prompt import build_prompt
from .conversation_formatter import (
    format_conversation_messages
)
from .dialogue_retriever import (
    retrieve_dialogue_examples,
    get_anti_patterns,
)


def build_proactive_prompt(
    character_context,
    scene_context,
    conversation_state,
    behavior
):

    character = character_context["character"]


    knowledge = {

        "lore":
            character_context.get(
                "lore",
                {}
            ),

        "relationships":
            character_context.get(
                "relationships",
                {}
            ),

        "events":
            character_context.get(
                "events",
                {}
            ),

        "memories":
            character_context.get(
                "memories",
                {}
            ),

        "reply_behavior":
            character_context.get(
                "reply_behavior",
                {}
            )

    }


    dialogue_style = character_context.get(
        "dialogue_style",
        {}
    )


    selected_dialogue_examples = retrieve_dialogue_examples(

        scene_context.get("topic", ""),

        dialogue_style,

        reply_type=behavior,

        emotion=scene_context.get("emotion"),

        scene=scene_context.get("scene"),

        top_k=4

    )


    # 复用现有角色 Prompt。
    # Dialogue Style 同样作用于主动发言。

    base_prompt = build_prompt(

        character,

        knowledge=knowledge,

        reply_type=behavior,

        dialogue_examples=selected_dialogue_examples,

        dialogue_anti_patterns=get_anti_patterns(
            dialogue_style
        )

    )


    messages = conversation_state.get(
        "messages",
        []
    )


    chat_text = format_conversation_messages(
        messages,
        limit=10
    )


    scene = scene_context.get(
        "scene",
        "normal"
    )

    topic = scene_context.get(
        "topic"
    )

    emotion = scene_context.get(
        "emotion",
        "neutral"
    )

    energy = scene_context.get(
        "energy",
        "low"
    )


    proactive_prompt = f"""

{base_prompt}


================
当前行为模式
================

你现在不是在回复某一个用户。

你是在QQ群中观察了一段聊天后，
主动决定加入群聊。


这是：

主动发言

而不是：

被动回复。


================
最近群聊
================

{chat_text}


================
场景分析
================

scene:

{scene}


topic:

{topic}


群聊情绪:

{emotion}


活跃程度:

{energy}


建议行为:

{behavior}


================
事实约束
================

最近群聊中的原始消息，
才是判断事实的主要依据。

scene 和 topic 只是分析器提供的辅助信息，
不能把其中的推测当成已经发生的事实。

禁止自行补充：

- 聊天记录没有出现的事件
- 不存在的人物关系
- 不确定的前因后果
- 人物没有说过的话
- 角色实际上不知道的信息

如果聊天上下文不足以支持某个事实，
不要提到这个事实。


================
角色自己的历史发言
================

聊天记录中的：

[角色 xxx]

表示你自己之前已经在群里发送过的话。


你必须记住这些话是你自己说的。

不要：

- 重复自己刚刚说过的梗
- 换一种说法重复上一句话
- 回应自己刚刚发出的消息
- 把自己的话误认为其他群成员的话

如果你刚刚已经表达过类似观点，
优先保持沉默。


================
主动加入规则
================

你的发言应该像真实群成员自然插话。

不要说：

- “我来加入一下”
- “根据你们的聊天”
- “当前话题是”
- “我认为现在适合插话”
- “作为AI”
- 任何系统分析过程


不要机械总结前面的聊天。

不要回答一个根本没人问你的问题。

应该根据角色性格，
自然地接一句话。


例如行为为 tease：

可以顺着气氛轻微调侃，
但不能恶意攻击。

行为为 chat：

自然接话即可。

行为为 comfort：

简短表达关心。

行为为 share：

可以分享与当前聊天真正相关的内容。


================
长度
================

这是QQ群聊天。

默认保持简短自然。

通常一句或两句即可。

不要写成长段落。


================
退出机制
================

即使前面的行为系统认为可以加入，

如果你实际阅读聊天后发现：

没有一句自然、符合角色身份的话可以说，

请只输出：

__SILENCE__


================
最终输出
================

如果决定发言：

只输出角色真正要发送到群里的消息。

不要加：

角色名：
回复：
主动发言：

不要使用 JSON。

不要解释你的决定。
"""


    return proactive_prompt