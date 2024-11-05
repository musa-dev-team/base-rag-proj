from dataclasses import dataclass
from datetime import datetime



@dataclass
class DuckieThreadMessage:
    channel_id: str = None
    thread_id: str = None
    message_id: str = None
    message_text: str = None
    files: list = None
    user: str = None
    timestamp: datetime = None
    url: str = None

    def __str__(self):
        return self.user + ":\n" + self.message_text

    def to_dict(self):
        return {
            "channel_id": self.channel_id,
            "thread_id": self.thread_id,
            "message_id": self.message_id,
            "url": self.url,
            "files": self.files,
            "user": self.user,
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            if self.timestamp
            else None,
            "message_text": self.message_text,
        }
    
    @property
    def __dict__(self):
        return {
            "channel_id": self.channel_id,
            "thread_id": self.thread_id,
            "message_id": self.message_id,
            "url": self.url,
            "files": self.files,
            "user": self.user,
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            if self.timestamp
            else None,
            "message_text": self.message_text,
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(**data)