from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass
class MediaContext:
    has_image: bool = False
    images: List[Dict[str, Any]] = field(default_factory=list)
    faces: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self):
        return {
            "has_image": self.has_image,
            "images": self.images,
            "faces": self.faces,
        }
