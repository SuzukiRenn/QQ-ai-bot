from .vision_result import VisionResult


def analyze_image(image_url: str) -> VisionResult:
    """
    Vision v3 interface.
    当前为 Mock 实现，等待接入真实视觉模型。
    """
    return VisionResult(
        description="图片等待视觉模型分析。",
        objects=[],
        scene="unknown",
        emotion="unknown",
        confidence=0.0,
    )
