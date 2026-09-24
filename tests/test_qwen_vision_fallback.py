import unittest
from bot.vision.vision_service import analyze_image_safe


class TestQwenVisionFallback(unittest.TestCase):

    def test_missing_api_does_not_crash(self):
        result = analyze_image_safe("test.jpg")
        self.assertIsNotNone(result)


if __name__ == "__main__":
    unittest.main()
