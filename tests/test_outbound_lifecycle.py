import unittest

from bot.conversation_state import (
    ConversationState
)

from bot.proactive_behavior import (
    ProactiveBehaviorEngine
)

from bot.message_result import (
    MessageResult
)

import bot.outbound_lifecycle as outbound_lifecycle

class TestConversationState(
    unittest.TestCase
):

    def setUp(self):

        self.state = ConversationState()


    def test_user_message_updates_active_users(
        self
    ):

        self.state.update(

            group_id="group_1",

            user_id="user_a",

            message="hello",

            sender_type="user"

        )


        state = self.state.get(
            "group_1"
        )


        self.assertEqual(
            len(state["messages"]),
            1
        )


        message = state[
            "messages"
        ][0]


        self.assertEqual(
            message["sender_type"],
            "user"
        )


        self.assertIn(
            "user_a",
            state["active_users"]
        )


    def test_character_message_not_in_active_users(
        self
    ):

        self.state.update(

            group_id="group_1",

            user_id="black_cat",

            message="喵",

            sender_type="character"

        )


        state = self.state.get(
            "group_1"
        )


        self.assertEqual(
            len(state["messages"]),
            1
        )


        message = state[
            "messages"
        ][0]


        self.assertEqual(
            message["sender_type"],
            "character"
        )


        self.assertNotIn(
            "black_cat",
            state["active_users"]
        )


class TestOutboundLifecycle(
    unittest.TestCase
):

    def setUp(self):

        # =====================
        # 保存 Runtime 原组件
        # =====================

        self.original_conversation_state = (
            outbound_lifecycle
            .runtime
            .conversation_state
        )


        self.original_proactive_behavior = (
            outbound_lifecycle
            .runtime
            .proactive_behavior
        )


        # =====================
        # 换成独立测试实例
        # 防止污染真实 Runtime
        # =====================

        self.conversation_state = (
            ConversationState()
        )


        self.proactive_behavior = (
            ProactiveBehaviorEngine()
        )


        outbound_lifecycle.runtime.conversation_state = (
            self.conversation_state
        )


        outbound_lifecycle.runtime.proactive_behavior = (
            self.proactive_behavior
        )


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


    def tearDown(self):

        # 恢复全局 Runtime

        outbound_lifecycle.runtime.conversation_state = (
            self.original_conversation_state
        )


        outbound_lifecycle.runtime.proactive_behavior = (
            self.original_proactive_behavior
        )


    def add_user_messages(
        self,
        group_id="group_1"
    ):

        self.conversation_state.update(

            group_id=group_id,

            user_id="user_a",

            message="message 1",

            sender_type="user"

        )


        self.conversation_state.update(

            group_id=group_id,

            user_id="user_b",

            message="message 2",

            sender_type="user"

        )


    # =====================
    # Commit
    # =====================

    def test_commit_proactive_message(
        self
    ):

        self.add_user_messages()


        result = MessageResult(

            action="proactive",

            content="猫看了都摇头喵",

            character_id="black_cat",

            behavior="tease",

            priority=80

        )


        committed = (
            outbound_lifecycle
            .commit_sent_message(
                "group_1",
                result
            )
        )


        self.assertTrue(
            committed
        )


        state = (
            self.conversation_state.get(
                "group_1"
            )
        )


        messages = list(
            state["messages"]
        )


        self.assertEqual(
            len(messages),
            3
        )


        last_message = messages[-1]


        self.assertEqual(
            last_message["user_id"],
            "black_cat"
        )


        self.assertEqual(
            last_message["message"],
            "猫看了都摇头喵"
        )


        self.assertEqual(
            last_message["sender_type"],
            "character"
        )


        # 角色不能算作 active user

        self.assertNotIn(
            "black_cat",
            state["active_users"]
        )


    def test_commit_activates_cooldown(
        self
    ):

        self.add_user_messages()


        result = MessageResult(

            action="proactive",

            content="喵",

            character_id="black_cat"

        )


        outbound_lifecycle.commit_sent_message(

            "group_1",

            result

        )


        state = (
            self.conversation_state.get(
                "group_1"
            )
        )


        precheck = (
            self.proactive_behavior.precheck(

                character_id="black_cat",

                character_package=
                    self.character_package,

                group_id="group_1",

                conversation_state=state

            )
        )


        self.assertIsNotNone(
            precheck
        )


        self.assertEqual(
            precheck["reason"],
            "cooldown"
        )


    def test_cooldown_does_not_affect_other_group(
        self
    ):

        self.add_user_messages(
            "group_a"
        )


        self.add_user_messages(
            "group_b"
        )


        result = MessageResult(

            action="proactive",

            content="喵",

            character_id="black_cat"

        )


        outbound_lifecycle.commit_sent_message(

            "group_a",

            result

        )


        state_a = (
            self.conversation_state.get(
                "group_a"
            )
        )


        state_b = (
            self.conversation_state.get(
                "group_b"
            )
        )


        result_a = (
            self.proactive_behavior.precheck(

                character_id="black_cat",

                character_package=
                    self.character_package,

                group_id="group_a",

                conversation_state=state_a

            )
        )


        result_b = (
            self.proactive_behavior.precheck(

                character_id="black_cat",

                character_package=
                    self.character_package,

                group_id="group_b",

                conversation_state=state_b

            )
        )


        self.assertEqual(
            result_a["reason"],
            "cooldown"
        )


        self.assertIsNone(
            result_b
        )


    # =====================
    # Invalid Commit
    # =====================

    def test_none_result_not_committed(
        self
    ):

        result = MessageResult(

            action="none",

            character_id="black_cat"

        )


        committed = (
            outbound_lifecycle
            .commit_sent_message(
                "group_1",
                result
            )
        )


        self.assertFalse(
            committed
        )


    def test_empty_content_not_committed(
        self
    ):

        result = MessageResult(

            action="proactive",

            content=None,

            character_id="black_cat"

        )


        committed = (
            outbound_lifecycle
            .commit_sent_message(
                "group_1",
                result
            )
        )


        self.assertFalse(
            committed
        )


    def test_reactive_message_also_starts_cooldown(
        self
    ):

        self.add_user_messages()


        result = MessageResult(

            action="reactive",

            content="当然可以喵",

            character_id="black_cat"

        )


        committed = (
            outbound_lifecycle
            .commit_sent_message(
                "group_1",
                result
            )
        )


        self.assertTrue(
            committed
        )


        state = (
            self.conversation_state.get(
                "group_1"
            )
        )


        precheck = (
            self.proactive_behavior.precheck(

                character_id="black_cat",

                character_package=
                    self.character_package,

                group_id="group_1",

                conversation_state=state

            )
        )


        self.assertEqual(
            precheck["reason"],
            "cooldown"
        )


if __name__ == "__main__":

    unittest.main()