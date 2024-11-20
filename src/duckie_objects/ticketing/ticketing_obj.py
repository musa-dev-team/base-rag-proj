import json
from dataclasses import dataclass
from datetime import datetime

from src.duckie_objects.ticketing.ticket_comment_obj import (
    DuckieTicketComment,
)


@dataclass
class DuckieTicket:
    ticket_id: str = ""
    title: str = ""
    description: str = ""
    url: str = ""
    user: str = ""
    comments: list[DuckieTicketComment] = None
    timestamp: datetime = None
    file_name: str = ""
    record_number: int = 0

    def format_ticket(self):
        return json.dumps(
            {
                "url": self.url,
                "timestamp": (
                    self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
                    if self.timestamp
                    else None
                ),
                "reporter": self.user,
                "title": self.title,
                "description": self.description,
                "discussion": [comment.format_comment() for comment in self.comments],
            }
        )

    @property
    def __dict__(self):
        return {
            "ticket_id": self.ticket_id,
            "title": self.title,
            "description": self.description,
            "url": self.url,
            "user": self.user,
            "comments": [comment.__dict__ for comment in self.comments],
            "timestamp": (
                self.timestamp.strftime("%Y-%m-%d %H:%M:%S") if self.timestamp else None
            ),
        }

    @classmethod
    def from_dict(cls, data):
        data['ticket_id'] = cls.get_unique_id(data)
        return cls(**data)
    
    @staticmethod
    def get_unique_id(data: dict) -> str:
        unique_id_components = {
            "type": "ticket",
            "file_name": data['file_name'],
            "record_number": data['record_number']
        }
        return str(unique_id_components["type"]) + "|" + str(unique_id_components["file_name"]) + "|" + str(unique_id_components["record_number"])
