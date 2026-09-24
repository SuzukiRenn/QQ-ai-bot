import sys
import types
import unittest

from bot.onebot_message_metadata import (
    extract_message_metadata,
    extract_reply_sender_user_id,
    apply_reply_sender,
)


class OneBotMetadataTests(unittest.TestCase):

    def test_at_other_member(self):
        metadata = extract_message_metadata({
            "self_id": 999,
            "message": [
                {"type": "at", "data": {"qq": "123"}},
                {"type": "text", "data": {"text": " 今晚玩吗"}},
            ],
        })

        self.assertFalse(metadata["at_bot"])
        self.assertEqual(metadata["at_other_users"], ["123"])

    def test_at_bot(self):
        metadata = extract_message_metadata({
            "self_id": 999,
            "message": [
                {"type": "at", "data": {"qq": "999"}},
                {"type": "text", "data": {"text": " 你怎么看"}},
            ],
        })

        self.assertTrue(metadata["at_bot"])
        self.assertEqual(metadata["at_other_users"], [])

    def test_at_bot_and_other(self):
        metadata = extract_message_metadata({
            "self_id": "999",
            "message": [
                {"type": "at", "data": {"qq": "123"}},
                {"type": "at", "data": {"qq": "999"}},
            ],
        })

        self.assertTrue(metadata["at_bot"])
        self.assertEqual(metadata["at_other_users"], ["123"])

    def test_at_all_is_not_other_user(self):
        metadata = extract_message_metadata({
            "self_id": "999",
            "message": [
                {"type": "at", "data": {"qq": "all"}},
            ],
        })

        self.assertTrue(metadata["at_all"])
        self.assertFalse(metadata["at_bot"])
        self.assertEqual(metadata["at_other_users"], [])

    def test_reply_segment_extracts_message_id(self):
        metadata = extract_message_metadata({
            "self_id": "999",
            "message": [
                {"type": "reply", "data": {"id": "1001"}},
                {"type": "text", "data": {"text": "你刚才说啥"}},
            ],
        })

        self.assertEqual(metadata["reply_message_id"], "1001")
        self.assertFalse(metadata["reply_to_bot"])
        self.assertIsNone(metadata["reply_sender_user_id"])

    def test_reply_seq_fallback(self):
        metadata = extract_message_metadata({
            "self_id": "999",
            "message": [
                {"type": "reply", "data": {"seq": 88}},
            ],
        })

        self.assertEqual(metadata["reply_message_id"], "88")


class ReplySenderResolutionTests(unittest.TestCase):

    def test_extract_sender_from_get_msg_response(self):
        sender_id = extract_reply_sender_user_id({
            "status": "ok",
            "retcode": 0,
            "data": {
                "sender": {
                    "user_id": 999,
                    "nickname": "bot",
                }
            },
        })

        self.assertEqual(sender_id, "999")

    def test_failed_get_msg_response_returns_none(self):
        sender_id = extract_reply_sender_user_id({
            "status": "failed",
            "retcode": 100,
            "data": None,
        })

        self.assertIsNone(sender_id)

    def test_apply_reply_sender_marks_bot(self):
        metadata = apply_reply_sender(
            {
                "reply_message_id": "1001",
                "reply_to_bot": False,
            },
            self_id="999",
            reply_sender_user_id="999",
        )

        self.assertTrue(metadata["reply_to_bot"])
        self.assertFalse(metadata["reply_to_other_user"])
        self.assertEqual(metadata["reply_sender_user_id"], "999")

    def test_apply_reply_sender_marks_other_user(self):
        metadata = apply_reply_sender(
            {
                "reply_message_id": "1001",
                "reply_to_bot": False,
            },
            self_id="999",
            reply_sender_user_id="123",
        )

        self.assertFalse(metadata["reply_to_bot"])
        self.assertTrue(metadata["reply_to_other_user"])
        self.assertEqual(metadata["reply_sender_user_id"], "123")


class TargetResolverMetadataTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # message_analyzer 只需要 llm.client 这个导入名。
        # 这些测试走 OneBot 确定性 early-return，不会调用 LLM。
        fake_llm = types.ModuleType("bot.llm")
        fake_llm.client = object()
        sys.modules["bot.llm"] = fake_llm

        from bot.message_analyzer import analyze_message
        cls.analyze_message = staticmethod(analyze_message)

    def test_at_other_forces_third_person(self):
        result = self.analyze_message(
            "[CQ:at,qq=123] 今晚玩吗",
            character_name="黑猫",
            character_aliases=["小黑猫"],
            chat_type="group",
            recent_messages=[],
            current_user_id="456",
            character_id="black_cat",
            message_metadata={
                "at_bot": False,
                "at_other_users": ["123"],
            },
        )

        self.assertEqual(result["target"], "third_person")
        self.assertEqual(result["confidence"], 1.0)

    def test_at_bot_forces_character(self):
        result = self.analyze_message(
            "[CQ:at,qq=999] 你怎么看",
            character_name="黑猫",
            character_aliases=["小黑猫"],
            chat_type="group",
            recent_messages=[],
            current_user_id="456",
            character_id="black_cat",
            message_metadata={
                "at_bot": True,
                "at_other_users": [],
            },
        )

        self.assertEqual(result["target"], "character")
        self.assertEqual(result["confidence"], 1.0)

    def test_at_bot_has_priority_when_both_exist(self):
        result = self.analyze_message(
            "同时@机器人和别人",
            character_name="黑猫",
            chat_type="group",
            message_metadata={
                "at_bot": True,
                "at_other_users": ["123"],
            },
        )

        self.assertEqual(result["target"], "character")

    def test_reply_to_bot_forces_character(self):
        result = self.analyze_message(
            "你刚才说啥",
            character_name="黑猫",
            character_aliases=["小黑猫"],
            chat_type="group",
            recent_messages=[],
            current_user_id="456",
            character_id="black_cat",
            message_metadata={
                "at_bot": False,
                "at_other_users": [],
                "reply_message_id": "1001",
                "reply_sender_user_id": "999",
                "reply_to_bot": True,
            },
        )

        self.assertEqual(result["target"], "character")
        self.assertEqual(result["confidence"], 1.0)

    def test_reply_to_bot_has_priority_over_at_other(self):
        result = self.analyze_message(
            "@别人 你们俩刚才说啥",
            character_name="黑猫",
            chat_type="group",
            message_metadata={
                "at_bot": False,
                "at_other_users": ["123"],
                "reply_message_id": "1001",
                "reply_sender_user_id": "999",
                "reply_to_bot": True,
            },
        )

        self.assertEqual(result["target"], "character")


if __name__ == "__main__":
    unittest.main()
