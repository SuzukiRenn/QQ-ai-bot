import unittest

from bot.proactive_behavior import (
    ProactiveBehaviorEngine
)


class TestProactiveBehaviorEngine(
    unittest.TestCase
):

    def setUp(self):

        # 每个测试重新创建 Engine
        # 避免 cooldown 状态互相污染
        self.engine = ProactiveBehaviorEngine()


        self.character_package = {

            "reply_behavior": {

                "reply_behavior": {

                    "proactive": {

                        "enabled": True,

                        "min_context_messages": 2,

                        "min_join_probability": 0.65,

                        "cooldown_seconds": 120

                    }

                }

            }

        }


    def make_state(
        self,
        user_message_count=2,
        character_message_count=0
    ):

        messages = []


        for i in range(
            user_message_count
        ):

            messages.append(

                {
                    "user_id":
                        f"user_{i}",

                    "message":
                        f"message_{i}",

                    "sender_type":
                        "user"
                }

            )


        for i in range(
            character_message_count
        ):

            messages.append(

                {
                    "user_id":
                        "black_cat",

                    "message":
                        f"character_message_{i}",

                    "sender_type":
                        "character"
                }

            )


        return {
            "messages": messages
        }


    # =====================
    # Precheck
    # =====================

    def test_insufficient_context(
        self
    ):

        state = self.make_state(
            user_message_count=1
        )


        result = self.engine.precheck(

            character_id="black_cat",

            character_package=
                self.character_package,

            group_id="10001",

            conversation_state=state

        )


        self.assertIsNotNone(
            result
        )

        self.assertFalse(
            result["should_speak"]
        )

        self.assertEqual(
            result["reason"],
            "insufficient_conversation_context"
        )

        self.assertEqual(
            result["message_count"],
            1
        )


    def test_enough_context_passes_precheck(
        self
    ):

        state = self.make_state(
            user_message_count=2
        )


        result = self.engine.precheck(

            character_id="black_cat",

            character_package=
                self.character_package,

            group_id="10001",

            conversation_state=state

        )


        self.assertIsNone(
            result
        )


    def test_character_messages_do_not_count(
        self
    ):

        state = self.make_state(

            user_message_count=1,

            character_message_count=5

        )


        result = self.engine.precheck(

            character_id="black_cat",

            character_package=
                self.character_package,

            group_id="10001",

            conversation_state=state

        )


        self.assertEqual(
            result["reason"],
            "insufficient_conversation_context"
        )

        self.assertEqual(
            result["message_count"],
            1
        )


    # =====================
    # Cooldown
    # =====================

    def test_cooldown_blocks_character(
        self
    ):

        state = self.make_state(
            user_message_count=3
        )


        self.engine.mark_speak(

            character_id="black_cat",

            group_id="10001"

        )


        result = self.engine.precheck(

            character_id="black_cat",

            character_package=
                self.character_package,

            group_id="10001",

            conversation_state=state

        )


        self.assertIsNotNone(
            result
        )

        self.assertEqual(
            result["reason"],
            "cooldown"
        )


    def test_cooldown_is_group_specific(
        self
    ):

        state = self.make_state(
            user_message_count=3
        )


        self.engine.mark_speak(

            character_id="black_cat",

            group_id="group_a"

        )


        result_a = self.engine.precheck(

            character_id="black_cat",

            character_package=
                self.character_package,

            group_id="group_a",

            conversation_state=state

        )


        result_b = self.engine.precheck(

            character_id="black_cat",

            character_package=
                self.character_package,

            group_id="group_b",

            conversation_state=state

        )


        self.assertEqual(
            result_a["reason"],
            "cooldown"
        )


        self.assertIsNone(
            result_b
        )


    # =====================
    # Scene Decision
    # =====================

    def test_high_probability_can_speak(
        self
    ):

        state = self.make_state(
            user_message_count=3
        )


        scene = {

            "scene": "funny",

            "topic": "game",

            "emotion": "happy",

            "energy": "medium",

            "join_probability": 0.8,

            "suggested_behavior": "tease"

        }


        result = self.engine.decide(

            character_id="black_cat",

            scene_context=scene,

            character_package=
                self.character_package,

            group_id="10001",

            conversation_state=state

        )


        self.assertTrue(
            result["should_speak"]
        )

        self.assertEqual(
            result["behavior"],
            "tease"
        )

        self.assertEqual(
            result["priority"],
            80
        )


    def test_low_probability_stays_silent(
        self
    ):

        state = self.make_state(
            user_message_count=3
        )


        scene = {

            "scene": "normal",

            "topic": "daily",

            "emotion": "neutral",

            "energy": "medium",

            "join_probability": 0.5,

            "suggested_behavior": "chat"

        }


        result = self.engine.decide(

            character_id="black_cat",

            scene_context=scene,

            character_package=
                self.character_package,

            group_id="10001",

            conversation_state=state

        )


        self.assertFalse(
            result["should_speak"]
        )

        self.assertEqual(
            result["reason"],
            "join_probability_below_threshold"
        )


    def test_low_energy_reduces_score(
        self
    ):

        state = self.make_state(
            user_message_count=3
        )


        scene = {

            "scene": "normal",

            "topic": "game",

            "emotion": "neutral",

            "energy": "low",

            "join_probability": 0.7,

            "suggested_behavior": "chat"

        }


        result = self.engine.decide(

            character_id="black_cat",

            scene_context=scene,

            character_package=
                self.character_package,

            group_id="10001",

            conversation_state=state

        )


        # 0.70 - 0.15 = 0.55
        self.assertFalse(
            result["should_speak"]
        )

        self.assertAlmostEqual(
            result["score"],
            0.55
        )


    def test_scene_can_recommend_observe(
        self
    ):

        state = self.make_state(
            user_message_count=3
        )


        scene = {

            "scene": "serious",

            "topic": "unknown",

            "emotion": "neutral",

            "energy": "medium",

            "join_probability": 0.9,

            "suggested_behavior": "observe"

        }


        result = self.engine.decide(

            character_id="black_cat",

            scene_context=scene,

            character_package=
                self.character_package,

            group_id="10001",

            conversation_state=state

        )


        self.assertFalse(
            result["should_speak"]
        )

        self.assertEqual(
            result["reason"],
            "scene_suggested_observe"
        )


    # =====================
    # Character Config
    # =====================

    def test_proactive_can_be_disabled(
        self
    ):

        package = {

            "reply_behavior": {

                "reply_behavior": {

                    "proactive": {

                        "enabled": False,

                        "min_context_messages": 2,

                        "min_join_probability": 0.65,

                        "cooldown_seconds": 120

                    }

                }

            }

        }


        state = self.make_state(
            user_message_count=5
        )


        result = self.engine.precheck(

            character_id="black_cat",

            character_package=package,

            group_id="10001",

            conversation_state=state

        )


        self.assertEqual(
            result["reason"],
            "proactive_disabled"
        )


if __name__ == "__main__":

    unittest.main()