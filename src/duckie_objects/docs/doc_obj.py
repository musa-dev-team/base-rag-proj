from dataclasses import dataclass
from datetime import datetime



@dataclass
class DuckieDoc:
    doc_id: str = ""
    content: str = ""
    url: str = ""
    timestamp: datetime = None

    @property
    def __dict__(self):
        timestamp = self.timestamp.strftime("%Y-%m-%d %H:%M:%S") if self.timestamp else None
        return {
            "doc_id": self.doc_id,
            "content": self.content,
            "url": self.url,
            "timestamp": timestamp,
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)
