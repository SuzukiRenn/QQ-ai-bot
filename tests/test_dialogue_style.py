import os
import tempfile
import unittest

from bot.character_loader import load_character_package
from bot.dialogue_formatter import format_dialogue_examples
from bot.dialogue_retriever import (
    get_anti_patterns,
    retrieve_dialogue_examples,
)
from bot.prompt import build_prompt
from bot.validators.dialogue_validator import validate_dialogue_style


class DialogueRetrieverTests(unittest.TestCase):

    def setUp(self):
        self.style = {
            "anti_patterns": ["不要复述用户消息"],
            "examples": [
                {
                    "id": "chat_1",
                    "reply_type": ["chat"],
                    "emotion": ["happy"],
                    "scene": ["group_chat"],
                    "keywords": ["蛋糕"],
                    "text": "这个看着就很香。",
                },
                {
                    "id": "tease_1",
                    "reply_type": ["tease"],
                    "text": "你还真敢说。",
                },
                {
                    "id": "generic_1",
                    "text": "嗯？",
                },
            ],
        }

    def test_reply_type_filters_mismatched_examples(self):
        results = retrieve_dialogue_examples(
            "这个蛋糕不错",
            self.style,
            reply_type="chat",
            emotion="happy",
            scene="group_chat",
            top_k=4,
        )
        ids = [item["id"] for item in results]
        self.assertIn("chat_1", ids)
        self.assertNotIn("tease_1", ids)

    def test_context_match_ranks_best_example_first(self):
        results = retrieve_dialogue_examples(
            "这个蛋糕不错",
            self.style,
            reply_type="chat",
            emotion="happy",
            scene="group_chat",
            top_k=4,
        )
        self.assertEqual(results[0]["id"], "chat_1")

    def test_anti_patterns_are_loaded(self):
        self.assertEqual(
            get_anti_patterns(self.style),
            ["不要复述用户消息"],
        )


class DialogueFormatterTests(unittest.TestCase):

    def test_formatter_separates_style_from_facts(self):
        text = format_dialogue_examples(
            [
                {
                    "id": "x",
                    "situation": "被调侃",
                    "style_tags": ["短句", "嘴硬"],
                    "text": "你还真敢说。",
                }
            ],
            ["不要复述用户消息"],
        )
        self.assertIn("只用于学习这个角色的说话方式", text)
        self.assertIn("直接复述或近似照抄", text)
        self.assertIn("不要复述用户消息", text)
        self.assertIn("你还真敢说。", text)


class DialogueLoaderAndPromptTests(unittest.TestCase):

    def test_character_loader_reads_optional_dialogue_style(self):
        package = load_character_package("dou_xian_man_tou")
        style = package.get("dialogue_style", {})
        self.assertTrue(style.get("examples"))
        self.assertTrue(style.get("anti_patterns"))

    def test_old_character_package_shape_stays_compatible(self):
        # loader 对缺失文件使用空 dict；这里验证 Prompt 本身也允许不传 Style。
        package = load_character_package("black_cat")
        prompt = build_prompt(
            package["character"],
            knowledge={
                "lore": package.get("lore", {}),
                "relationships": package.get("relationships", {}),
                "events": package.get("events", {}),
                "memories": package.get("memories", {}),
                "reply_behavior": package.get("reply_behavior", {}),
            },
            reply_type="chat",
        )
        self.assertIn(package["character"]["meta"]["name"], prompt)

    def test_prompt_injects_selected_style_examples(self):
        package = load_character_package("dou_xian_man_tou")
        style = package["dialogue_style"]
        examples = retrieve_dialogue_examples(
            "今晚吃什么",
            style,
            reply_type="answer",
            emotion="normal",
            scene="group_chat",
        )
        prompt = build_prompt(
            package["character"],
            knowledge={
                "lore": package.get("lore", {}),
                "relationships": package.get("relationships", {}),
                "events": package.get("events", {}),
                "memories": package.get("memories", {}),
                "reply_behavior": package.get("reply_behavior", {}),
            },
            reply_type="answer",
            dialogue_examples=examples,
            dialogue_anti_patterns=get_anti_patterns(style),
        )
        self.assertIn("角色语言示范", prompt)
        self.assertIn("牛肉面", prompt)
        self.assertIn("不要先复述用户刚说过的话再回应", prompt)


class DialogueValidatorTests(unittest.TestCase):

    def test_valid_dialogue_file(self):
        content = """
dialogue_style:
  anti_patterns:
    - 不要复述
  examples:
    - id: demo_1
      reply_type: chat
      text: 这句只是示范。
"""
        with tempfile.NamedTemporaryFile(
            "w",
            suffix=".yaml",
            encoding="utf-8",
            delete=False,
        ) as f:
            f.write(content)
            path = f.name

        try:
            self.assertEqual(validate_dialogue_style(path), [])
        finally:
            os.unlink(path)

    def test_duplicate_ids_are_rejected(self):
        content = """
dialogue_style:
  examples:
    - id: demo_1
      text: 第一条
    - id: demo_1
      text: 第二条
"""
        with tempfile.NamedTemporaryFile(
            "w",
            suffix=".yaml",
            encoding="utf-8",
            delete=False,
        ) as f:
            f.write(content)
            path = f.name

        try:
            errors = validate_dialogue_style(path)
            self.assertTrue(any("duplicate" in item for item in errors))
        finally:
            os.unlink(path)


if __name__ == "__main__":
    unittest.main()
