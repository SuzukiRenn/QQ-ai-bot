import unittest
from bot.vision.vision_analyzer import analyze_image

class TestVisionResult(unittest.TestCase):
    def test_mock_vision(self):
        result = analyze_image("test.jpg")
        self.assertTrue(hasattr(result, "description"))

if __name__ == "__main__":
    unittest.main()
