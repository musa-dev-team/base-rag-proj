from dataclasses import dataclass
from datetime import datetime



@dataclass
class DuckieTicketComment:
    comment_id: str = ""
    content: str = ""
    timestamp: datetime = None
    user: str = ""
    url: str = ""

    def format_comment(self):
        return {
            "content": self.content,
            "timestamp": (
                self.timestamp.strftime("%Y-%m-%d %H:%M:%S") if self.timestamp else None
            ),
            "user": self.user,
        }

    @property
    def __dict__(self):
        return {
            "comment_id": self.comment_id,
            "content": self.content,
            "timestamp": (
                self.timestamp.strftime("%Y-%m-%d %H:%M:%S") if self.timestamp else None
            ),
            "user": self.user,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)
