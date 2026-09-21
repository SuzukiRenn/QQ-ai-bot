import json
from typing import Dict, Any

from .ai import ask_llm
from .conversation_formatter import (
    format_conversation_messages
)


class SceneAnalyzer:
    """
    群聊场景分析器

    输入:
        conversation state
        character context

    输出:
        标准化 scene context
    """


    def analyze(
        self,
        conversation_state: Dict[str, Any],
        character_context: Dict[str, Any] | None = None
    ):

        messages = list(
            conversation_state.get(
                "messages",
                []
            )
        )


        if not messages:
            return self.empty_result()


        # 不需要每次把全部20条都交给模型
        messages = messages[-10:]


        prompt = self.build_prompt(
            messages,
            character_context
        )


        try:

            result = ask_llm(
                prompt
            )

        except Exception as e:

            print(
                "Scene Analyzer LLM Error:",
                e
            )

            return self.fallback_result(
                "llm_error"
            )


        return self.parse_result(
            result
        )


    def build_prompt(
        self,
        messages,
        character_context
    ):

        chat_text = format_conversation_messages(
            messages,
            limit=10
        )

        character = {}

        if character_context:

            character = character_context.get(
                "character",
                {}
            )


        return f"""
你是QQ群聊天场景分析器。

你的任务不是回复消息，
而是分析当前群聊环境，并判断角色是否适合主动加入聊天。


====================
最近群聊
====================

{chat_text}


====================
角色信息
====================

{character}


====================
事实约束
====================

只能根据提供的聊天记录分析。

禁止补充聊天记录中没有明确出现的事实。

不要自行猜测：

- 人物之间发生过什么
- “打”具体指打架、打游戏还是其他事情
- 未明确出现的地点
- 未明确出现的关系
- 未明确出现的事件

如果信息不足：

topic 应使用保守、概括的描述。

例如：

聊天：

“他俩昨天打得也太搞笑了哈哈哈哈。”

如果没有更多上下文，

不要推断为：

“昨天两人打架”

应该使用类似：

“昨天两人的搞笑事件”

或：

“前文提到的搞笑事情”


====================
说话者身份
====================

聊天记录中：

[群成员 xxx]

表示真实QQ群成员的消息。


[角色 xxx]

表示当前AI角色自己之前已经发送过的消息。


分析群聊时必须考虑角色刚刚说过什么。

不要：

- 把角色自己的发言误认为群成员发言
- 重复角色刚刚说过的内容
- 对角色自己的上一句话进行自我回复
- 假装角色不知道自己刚刚说过什么


====================
需要分析
====================

scene:
当前聊天场景，例如：

normal
funny
serious
emotional
conflict
quiet


topic:
当前主要话题。


emotion:
当前群聊整体情绪，例如：

neutral
happy
sad
angry
excited


energy:
聊天活跃程度：

low
medium
high


join_probability:
角色此时主动加入聊天是否自然。

范围：

0.0 - 1.0


suggested_behavior:
如果加入，建议采用什么行为。

例如：

chat
comfort
tease
share
greet
observe


====================
返回格式
====================

只返回 JSON。

不要解释。
不要使用 Markdown。
不要使用 ```json。

格式：

{{
    "scene": "normal",
    "topic": "",
    "emotion": "neutral",
    "energy": "medium",
    "join_probability": 0.0,
    "suggested_behavior": "observe"
}}
"""


    def parse_result(
        self,
        result
    ):

        if isinstance(
            result,
            dict
        ):

            data = result

        else:

            text = str(
                result
            ).strip()


            # 防止模型偶尔还是返回 ```json
            if text.startswith("```"):

                lines = text.splitlines()

                if lines:
                    lines = lines[1:]

                if lines and lines[-1].strip() == "```":
                    lines = lines[:-1]

                text = "\n".join(
                    lines
                ).strip()


            # 如果前后混入了少量解释，
            # 尝试只截取 JSON 对象
            start = text.find("{")
            end = text.rfind("}")


            if start != -1 and end != -1:

                text = text[
                    start:end + 1
                ]


            try:

                data = json.loads(
                    text
                )

            except Exception as e:

                print(
                    "Scene Analyzer JSON Error:",
                    e
                )

                print(
                    "Raw Scene Result:",
                    result
                )

                return self.fallback_result(
                    "invalid_json"
                )


        try:

            probability = float(
                data.get(
                    "join_probability",
                    0
                )
            )

        except (TypeError, ValueError):

            probability = 0


        probability = max(
            0.0,
            min(
                probability,
                1.0
            )
        )


        return {

            "scene":
                data.get(
                    "scene",
                    "normal"
                ),

            "topic":
                data.get(
                    "topic"
                ),

            "emotion":
                data.get(
                    "emotion",
                    "neutral"
                ),

            "energy":
                data.get(
                    "energy",
                    "low"
                ),

            "join_probability":
                probability,

            "suggested_behavior":
                data.get(
                    "suggested_behavior",
                    "observe"
                )

        }


    def empty_result(self):

        return {

            "scene": "empty",

            "topic": None,

            "emotion": "neutral",

            "energy": "low",

            "join_probability": 0.0,

            "suggested_behavior": "observe"

        }


    def fallback_result(
        self,
        reason
    ):

        return {

            "scene": "unknown",

            "topic": None,

            "emotion": "neutral",

            "energy": "low",

            "join_probability": 0.0,

            "suggested_behavior": "observe",

            "fallback_reason": reason

        }


scene_analyzer = SceneAnalyzer()