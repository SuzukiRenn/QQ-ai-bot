from typing import Dict, Any

from bot.llm import chat_completion


class SceneAnalyzer:
    """
    群聊场景分析器

    输入:
        conversation state
        character context

    输出:
        scene context
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



        prompt = self.build_prompt(
            messages,
            character_context
        )


        result = chat_completion(
            prompt
        )


        return self.parse_result(
            result
        )



    def build_prompt(
        self,
        messages,
        character_context
    ):


        chat_text = "\n".join(

            [
                f"{m['user_id']}: {m['message']}"

                for m in messages

            ]

        )


        return f"""
你是一个群聊场景分析器。

分析下面聊天：

{chat_text}


请输出 JSON:

{{
 "scene":"",
 "topic":"",
 "emotion":"",
 "energy":"",
 "join_probability":0,
 "suggested_behavior":""
}}


角色信息:

{character_context}

要求：

- 不生成回复
- 只分析是否适合角色参与
- join_probability范围0-1
"""



    def parse_result(
        self,
        result
    ):

        """
        后续增加 JSON schema 校验
        """

        return result



    def empty_result(self):

        return {

            "scene":"empty",

            "topic":None,

            "emotion":"neutral",

            "energy":"low",

            "join_probability":0,

            "suggested_behavior":None

        }



scene_analyzer = SceneAnalyzer()