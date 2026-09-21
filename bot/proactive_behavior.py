from typing import Dict, Any
import time


class ProactiveBehaviorEngine:
    """
    主动行为决策引擎
    """

    DEFAULT_THRESHOLD = 0.65
    DEFAULT_COOLDOWN = 120


    def __init__(self):

        self.last_active = {}


    # =====================
    # 配置读取
    # =====================

    def get_proactive_config(
        self,
        character_package
    ):

        raw_behavior = character_package.get(
            "reply_behavior",
            {}
        )

        behavior = raw_behavior.get(
            "reply_behavior",
            raw_behavior
        )

        return behavior.get(
            "proactive",
            {}
        )


    # =====================
    # Cheap Precheck
    # =====================

    def precheck(
        self,
        character_id: str,
        character_package: Dict[str, Any],
        group_id: str | None = None,
        conversation_state: Dict[str, Any] | None = None
    ):
        """
        在调用 SceneAnalyzer / LLM 之前执行。

        返回:
            None
                可以继续进行场景分析

            dict
                已经可以确定不应该主动发言
        """

        proactive = self.get_proactive_config(
            character_package
        )


        # =====================
        # 1. 是否启用主动行为
        # =====================

        if proactive.get(
            "enabled",
            True
        ) is False:

            return self.reject(
                "proactive_disabled"
            )


        # =====================
        # 2. 用户消息数量
        # =====================
        #
        # 注意：
        # 不能把角色自己的消息算进去。
        # =====================

        messages = []

        if conversation_state:

            messages = list(
                conversation_state.get(
                    "messages",
                    []
                )
            )


        user_messages = [

            message

            for message in messages

            if message.get(
                "sender_type",
                "user"
            ) == "user"

        ]


        message_count = len(
            user_messages
        )


        min_context_messages = proactive.get(
            "min_context_messages",
            2
        )


        if message_count < min_context_messages:

            return self.reject(

                "insufficient_conversation_context",

                message_count=message_count,

                required_messages=min_context_messages

            )


        # =====================
        # 3. Cooldown
        # =====================

        cooldown = proactive.get(
            "cooldown_seconds",
            self.DEFAULT_COOLDOWN
        )


        if not self.can_speak(
            character_id,
            group_id,
            cooldown
        ):

            return self.reject(
                "cooldown"
            )


        # 可以继续调用 SceneAnalyzer

        return None


    # =====================
    # 完整主动决策
    # =====================

    def decide(
        self,
        character_id: str,
        scene_context: Dict[str, Any],
        character_package: Dict[str, Any],
        emotion_context: Dict[str, Any] | None = None,
        relationship_context: Dict[str, Any] | None = None,
        group_id: str | None = None,
        conversation_state: Dict[str, Any] | None = None
    ):

        # 再做一次防御性检查
        # 即使以后其他代码直接调用 decide()
        # 也不会绕开基础规则。

        precheck_result = self.precheck(

            character_id=character_id,

            character_package=character_package,

            group_id=group_id,

            conversation_state=conversation_state

        )


        if precheck_result is not None:

            return precheck_result


        proactive = self.get_proactive_config(
            character_package
        )


        threshold = proactive.get(
            "min_join_probability",
            self.DEFAULT_THRESHOLD
        )


        # =====================
        # 场景信息
        # =====================

        probability = scene_context.get(
            "join_probability",
            0
        )

        energy = scene_context.get(
            "energy",
            "low"
        )

        suggested_behavior = scene_context.get(
            "suggested_behavior",
            "observe"
        )


        try:

            score = float(
                probability
            )

        except (TypeError, ValueError):

            score = 0.0


        # =====================
        # 场景修正
        # =====================

        if energy == "low":

            score -= 0.15


        if suggested_behavior == "observe":

            return self.reject(
                "scene_suggested_observe"
            )


        score = max(
            0.0,
            min(
                score,
                1.0
            )
        )


        # =====================
        # 阈值判断
        # =====================

        if score < threshold:

            return {

                "should_speak": False,

                "behavior": "observe",

                "priority": int(
                    score * 100
                ),

                "reason":
                    "join_probability_below_threshold",

                "score": score,

                "threshold": threshold

            }


        # =====================
        # 行为选择
        # =====================

        allowed_behaviors = {

            "chat",
            "comfort",
            "tease",
            "share",
            "greet"

        }


        if suggested_behavior in allowed_behaviors:

            action = suggested_behavior

        else:

            action = "chat"


        return {

            "should_speak": True,

            "behavior": action,

            "priority": int(
                score * 100
            ),

            "reason":
                "scene_suitable_for_proactive_join",

            "score": score,

            "threshold": threshold

        }


    # =====================
    # Cooldown
    # =====================

    def _cooldown_key(
        self,
        character_id,
        group_id
    ):

        if group_id:

            return (
                f"{group_id}:"
                f"{character_id}"
            )

        return character_id


    def can_speak(
        self,
        character_id,
        group_id=None,
        cooldown=None
    ):

        if cooldown is None:

            cooldown = self.DEFAULT_COOLDOWN


        key = self._cooldown_key(
            character_id,
            group_id
        )


        now = time.time()


        last = self.last_active.get(
            key,
            0
        )


        return (
            now - last
            >= cooldown
        )


    def mark_speak(
        self,
        character_id,
        group_id=None
    ):

        key = self._cooldown_key(
            character_id,
            group_id
        )


        self.last_active[
            key
        ] = time.time()


    # =====================
    # Reject
    # =====================

    def reject(
        self,
        reason,
        **extra
    ):

        result = {

            "should_speak": False,

            "behavior": "observe",

            "priority": 0,

            "reason": reason

        }


        result.update(
            extra
        )


        return result


proactive_behavior = ProactiveBehaviorEngine()