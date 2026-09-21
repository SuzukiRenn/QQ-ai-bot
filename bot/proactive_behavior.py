from typing import Dict, Any
import time



class ProactiveBehaviorEngine:
    """
    主动行为决策引擎

    决定角色是否主动发言
    """



    def __init__(self):

        # 记录角色最后主动发言时间

        self.last_active = {}



    def decide(
        self,
        character_id: str,
        scene_context: Dict[str, Any],
        character_package: Dict[str, Any],
        emotion_context: Dict[str, Any] | None = None,
        relationship_context: Dict[str, Any] | None = None
    ):


        # 1. 基础检查

        if not self.can_speak(
            character_id
        ):

            return self.reject(
                "cooldown"
            )



        # 2. 场景概率判断

        probability = scene_context.get(
            "join_probability",
            0
        )


        if probability < 0.5:

            return self.reject(
                "scene_not_suitable"
            )



        # 3. 读取角色行为偏好

        behavior = character_package.get(
            "reply_behavior",
            {}
        )


        proactive = behavior.get(
            "proactive",
            {}
        )


        # 4. 兴趣匹配

        topic = scene_context.get(
            "topic"
        )


        interests = proactive.get(
            "preferred_topics",
            []
        )


        if topic in interests:

            priority = 80

            action = "share"


        else:

            priority = 50

            action = "casual_join"



        return {

            "should_speak": True,

            "behavior": action,

            "priority": priority,

            "reason":
                "scene matched character behavior"

        }



    def can_speak(
        self,
        character_id
    ):

        now = time.time()


        last = self.last_active.get(
            character_id,
            0
        )


        # 默认30秒冷却

        if now-last < 30:

            return False


        return True



    def mark_speak(
        self,
        character_id
    ):

        self.last_active[character_id] = time.time()



    def reject(
        self,
        reason
    ):

        return {

            "should_speak":False,

            "reason":reason

        }




proactive_behavior = ProactiveBehaviorEngine()