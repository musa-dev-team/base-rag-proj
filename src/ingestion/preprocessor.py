from typing import Dict, Any
from abc import ABC, abstractmethod
from src.duckie_objects.threads.thread_obj import DuckieThread
from src.duckie_objects.docs.doc_obj import DuckieDoc
from src.duckie_objects.ticketing.ticketing_obj import DuckieTicket


class DataPreprocessor(ABC):
    @abstractmethod
    def preprocess(self, data: Any) -> Dict[str, Any]:
        pass

class ThreadPreprocessor(DataPreprocessor):
    def preprocess(self, thread: DuckieThread) -> Dict[str, Any]:
        return {
            "type": "thread",
            "id": thread.thread_id,
            "content": thread.format_thread(),
            "url": thread.url,
            "timestamp": thread.timestamp.isoformat() if thread.timestamp else None,
            "message_count": len(thread.messages) if thread.messages else 0
        }

class DocPreprocessor(DataPreprocessor):
    def preprocess(self, doc: DuckieDoc) -> Dict[str, Any]:
        return {
            "type": "doc",
            "id": doc.doc_id,
            "title": doc.title,
            "html": doc.html,
            "content": doc.content,
            "url": doc.url,
            "timestamp": doc.timestamp.isoformat() if doc.timestamp else None
        }

class TicketPreprocessor(DataPreprocessor):
    def preprocess(self, ticket: DuckieTicket) -> Dict[str, Any]:
        return {
            "type": "ticket",
            "id": ticket.ticket_id,
            "title": ticket.title,
            "content": ticket.format_ticket(),
            "url": ticket.url,
            "user": ticket.user,
            "timestamp": ticket.timestamp.isoformat() if ticket.timestamp else None,
            "comment_count": len(ticket.comments) if ticket.comments else 0
        }