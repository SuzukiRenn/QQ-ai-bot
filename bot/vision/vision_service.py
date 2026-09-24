from .vision_analyzer import analyze_image
from .providers.qwen_provider import analyze_with_qwen


def analyze_image_safe(image_url: str):
    """
    Vision service with graceful fallback.

    API失败不会影响机器人主流程。
    """

    result = analyze_with_qwen(image_url)

    if result is not None:
        return result

    return analyze_image(image_url)
