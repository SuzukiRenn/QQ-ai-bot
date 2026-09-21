from dataclasses import dataclass
from typing import Optional


@dataclass
class MessageResult:

    action: str

    # reactive
    # proactive
    # none

    content: Optional[str] = None

    character_id: Optional[str] = None

    behavior: Optional[str] = None

    priority: int = 0


    @property
    def should_send(self):

        return (
            self.action
            in {
                "reactive",
                "proactive"
            }
            and bool(
                self.content
            )
        )