from dataclasses import dataclass
from datetime import datetime



@dataclass
class DuckieDoc:
    doc_id: str = ""
    title: str = ""
    html: str = ""
    content: str = ""
    url: str = ""
    timestamp: datetime = None
    file_name: str = ""  
    record_number: int = 0  

    def format_doc(self):
        return "\n".join([str(self.title), str(self.content), "URL:" + str(self.url)])

    @property
    def __dict__(self):
        timestamp = self.timestamp.strftime("%Y-%m-%d %H:%M:%S") if self.timestamp else None
        return {
            "doc_id": self.doc_id,
            "title": self.title,
            "content": self.content,
            "url": self.url,
            "timestamp": timestamp,
            "file_name": self.file_name,
            "record_number": self.record_number
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        data['doc_id'] = cls.get_unique_id(data)
        return cls(**data)
    
    @staticmethod
    def get_unique_id(data: dict) -> str:
        unique_id_components = {
            "type": "doc",
            "file_name": data['file_name'],
            "record_number": data['record_number']
        }
        return str(unique_id_components["type"]) + "|" + str(unique_id_components["file_name"]) + "|" + str(unique_id_components["record_number"])
