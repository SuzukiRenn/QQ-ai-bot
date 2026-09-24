import os
from openai import OpenAI

from ..vision_result import VisionResult


def analyze_with_qwen(image_url: str) -> VisionResult | None:
    """
    Qwen3-VL-Flash provider.

    失败时返回 None，由上层降级。
    不影响机器人文字聊天。
    """

    api_key = os.getenv("DASHSCOPE_API_KEY")

    if not api_key:
        return None

    try:
        client = OpenAI(
            api_key=api_key,
            base_url="https://maas.qianwenaiapi.com/compatible-mode/v1"
        )

        completion = client.chat.completions.create(
            model=os.getenv(
                "VISION_MODEL",
                "qwen3-vl-flash"
            ),
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_url
                            }
                        },
                        {
                            "type": "text",
                            "text": (
                                "分析图片内容。"
                                "返回简短描述、主要对象、场景和可能情绪。"
                            )
                        }
                    ]
                }
            ],
            extra_body={
                "enable_thinking": False
            }
        )

        text = completion.choices[0].message.content or ""

        return VisionResult(
            description=text,
            objects=[],
            scene="",
            emotion="",
            confidence=0.5,
        )

    except Exception:
        return None
