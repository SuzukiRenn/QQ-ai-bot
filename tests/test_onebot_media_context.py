import unittest

from bot.media.onebot_media_parser import parse_onebot_message_segments


class TestOneBotMediaContext(unittest.TestCase):

    def test_image(self):
        ctx = parse_onebot_message_segments([
            {
                "type": "image",
                "data": {
                    "file": "cat.jpg",
                    "url": "http://example.com/cat.jpg"
                }
            }
        ])
        self.assertTrue(ctx.has_image)

    def test_face(self):
        ctx = parse_onebot_message_segments([
            {
                "type": "face",
                "data": {
                    "id": "178"
                }
            }
        ])
        self.assertEqual(ctx.faces[0]["id"], "178")


if __name__ == "__main__":
    unittest.main()
