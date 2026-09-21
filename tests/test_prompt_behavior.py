import unittest

from bot.character_loader import (
    load_character_package
)

from bot.prompt import (
    build_prompt
)


class TestPromptBehavior(
    unittest.TestCase
):

    def test_tease_behavior_in_prompt(
        self
    ):

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


                character = package[
                    "character"
                ]


                knowledge = {

                    "lore":
                        package.get(
                            "lore",
                            {}
                        ),

                    "relationships":
                        package.get(
                            "relationships",
                            {}
                        ),

                    "events":
                        package.get(
                            "events",
                            {}
                        ),

                    "memories":
                        package.get(
                            "memories",
                            {}
                        ),

                    "reply_behavior":
                        package.get(
                            "reply_behavior",
                            {}
                        )

                }


                # 使用固定测试数据，
                # 不读取真实用户情绪状态。

                emotion_context = {

                    "long_term": {
                        "happiness": 60
                    },

                    "current": {
                        "happiness": 50
                    },

                    "mood": "happy"

                }


                prompt = build_prompt(

                    character=character,

                    knowledge=knowledge,

                    relationship={
                        "trust": 70,
                        "intimacy": 70,
                        "familiarity": 70
                    },

                    relationship_level="friend",

                    reply_type="tease",

                    emotion_context=
                        emotion_context

                )


                # =====================
                # Character
                # =====================

                self.assertIn(
                    character[
                        "meta"
                    ][
                        "name"
                    ],
                    prompt
                )


                # =====================
                # Reply Type
                # =====================

                self.assertIn(
                    "tease",
                    prompt
                )


                tease_behavior = (
                    package[
                        "reply_behavior"
                    ][
                        "reply_type_behavior"
                    ][
                        "tease"
                    ]
                )


                description = (
                    tease_behavior.get(
                        "description"
                    )
                )


                if description:

                    self.assertIn(
                        description,
                        prompt
                    )


                for rule in (
                    tease_behavior.get(
                        "rules",
                        []
                    )
                ):

                    self.assertIn(
                        rule,
                        prompt
                    )


                # =====================
                # Relationship
                # =====================

                friend_behavior = (
                    package[
                        "reply_behavior"
                    ][
                        "relationship_behavior"
                    ][
                        "friend"
                    ]
                )


                friend_description = (
                    friend_behavior.get(
                        "description"
                    )
                )


                if friend_description:

                    self.assertIn(
                        friend_description,
                        prompt
                    )


                # =====================
                # Emotion
                # =====================

                self.assertIn(
                    "角色心理状态",
                    prompt
                )


                # =====================
                # World Knowledge
                # =====================

                self.assertIn(
                    "世界观知识",
                    prompt
                )


if __name__ == "__main__":

    unittest.main()