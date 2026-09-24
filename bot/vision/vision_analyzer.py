from .vision_result import VisionResult


def analyze_image(image_url: str) -> VisionResult:
    """
    Vision fallback implementation.

    当视觉API不可用时返回安全结果。
    """

    return VisionResult(
        description="图片暂时无法分析。",
        objects=[],
        scene="unknown",
        emotion="unknown",
        confidence=0.0,
    )
