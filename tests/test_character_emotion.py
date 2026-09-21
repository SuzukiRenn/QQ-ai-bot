import os
import tempfile
import unittest

from bot.character_loader import (
    load_character_package
)

from bot import character_emotion


class TestCharacterEmotion(
    unittest.TestCase
):

    def setUp(self):

        # 使用临时文件保存测试情绪画像，
        # 防止污染项目真实的
        # character_emotion_profile.json

        self.temp_dir = (
            tempfile.TemporaryDirectory()
        )

        self.original_profile_file = (
            character_emotion.PROFILE_FILE
        )

        character_emotion.PROFILE_FILE = (
            os.path.join(
                self.temp_dir.name,
                "character_emotion_profile.json"
            )
        )


    def tearDown(self):

        character_emotion.PROFILE_FILE = (
            self.original_profile_file
        )

        self.temp_dir.cleanup()


    def test_generate_character_emotion(
        self
    ):

        required_emotions = {

            "black_cat": {
                "nostalgia",
                "happiness"
            },

            "maomao": {
                "curiosity",
                "confidence"
            }

        }


        for character_id in (
            "black_cat",
            "maomao"
        ):

            with self.subTest(
                character_id=character_id
            ):

                package = (
                    load_character_package(
                        character_id
                    )
                )


                memories = package.get(
                    "memories",
                    {}
                )


                emotion = (
                    character_emotion
                    .generate_character_emotion(
                        character_id,
                        memories
                    )
                )


                self.assertIsInstance(
                    emotion,
                    dict
                )


                self.assertTrue(
                    emotion
                )


                # 所有长期情绪值都应该
                # 在 0 - 100 范围内

                for value in emotion.values():

                    self.assertGreaterEqual(
                        value,
                        0
                    )

                    self.assertLessEqual(
                        value,
                        100
                    )


                # 检查角色的核心长期情绪
                # 是否从 memories.yaml 中产生

                for emotion_name in (
                    required_emotions[
                        character_id
                    ]
                ):

                    self.assertIn(
                        emotion_name,
                        emotion
                    )


                # 检查保存之后是否能够读取回来

                saved_emotion = (
                    character_emotion
                    .get_character_emotion(
                        character_id
                    )
                )


                self.assertEqual(
                    saved_emotion,
                    emotion
                )


if __name__ == "__main__":

    unittest.main()