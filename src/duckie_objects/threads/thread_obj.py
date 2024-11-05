from dataclasses import dataclass
from datetime import datetime

from src.duckie_objects.threads.thread_message_obj import (
    DuckieThreadMessage,
)


@dataclass
class DuckieThread:
    thread_id: str = ""
    messages: list[DuckieThreadMessage] = None
    url: str = ""
    timestamp: datetime = None

    def format_thread(self):
        return "\n".join(str(msg) for msg in self.messages)
    
    @property
    def __dict__(self):
        timestamp = self.timestamp.strftime("%Y-%m-%d %H:%M:%S") if self.timestamp else None

        return {
            "thread_id": self.thread_id,
            "messages": [msg.__dict__ for msg in self.messages or []],
            "url": self.url,
            "timestamp": timestamp,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)