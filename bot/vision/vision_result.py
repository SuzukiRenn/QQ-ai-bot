from dataclasses import dataclass, field
from typing import List


@dataclass
class VisionResult:
    description: str = ""
    objects: List[str] = field(default_factory=list)
    scene: str = ""
    emotion: str = ""
    confidence: float = 0.0

    def to_dict(self):
        return {
            "description": self.description,
            "objects": self.objects,
            "scene": self.scene,
            "emotion": self.emotion,
            "confidence": self.confidence,
        }
