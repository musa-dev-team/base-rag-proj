from abc import ABC , abstractmethod
from typing import List, Any , Dict
import os 
from datetime import datetime
import json
from src.duckie_objects.docs.doc_obj import DuckieDoc
from src.duckie_objects.threads.thread_message_obj import DuckieThreadMessage
from src.duckie_objects.threads.thread_obj import DuckieThread
from src.duckie_objects.ticketing.ticket_comment_obj import DuckieTicketComment
from src.duckie_objects.ticketing.ticketing_obj import DuckieTicket
from src.ingestion.extractor import CommentExtractor 


class ContentLoader(ABC):
    @abstractmethod
    def load(self, file_path: str) -> List[Any]:
        pass

    @staticmethod
    def _get_file_name(file_path: str) -> str:
        return os.path.basename(file_path)


class ContentLoaderFactory:
    @staticmethod
    def get_loader(content_type: str) -> ContentLoader:
        if content_type == "thread":
            return ThreadLoader()
        elif content_type == "doc":
            return DocLoader()
        elif content_type == "ticket":
            return TicketLoader()
        else:
            raise ValueError(f"Unknown content type: {content_type}")


class ThreadLoader(ContentLoader):
    def load(self, file_path: str) -> List[DuckieThread]:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        threads = []
        file_name = self._get_file_name(file_path)
        
        for enum, item in enumerate(data):
            if "thread" in item and item["thread"] is not None:
                thread_messages = self._create_thread_messages(item, enum, file_name)
                thread = self._create_thread(item, enum, file_name, thread_messages)
                threads.append(thread)
            
        return threads

    def _create_thread_messages(self, item: Dict[str, Any], enum: int, file_name: str) -> List[DuckieThreadMessage]:
        thread_messages = []

        for idx, msg in enumerate(item["thread"]):
            msg_dict = {
                "thread_id": str(enum),
                "message_id": str(idx),
                "file_name": file_name,
                "message_text": str(msg["message_content"]),
                "url": item["url"],
                "user": msg["user_name"],
                **{k: v for k, v in msg.items() if k not in ["user_name", "message_content"]}
            }
            thread_messages.append(DuckieThreadMessage.from_dict(msg_dict))
        return thread_messages

    def _create_thread(self, item: Dict[str, Any], enum: int, file_name: str, thread_messages: List[DuckieThreadMessage]) -> DuckieThread:
        thread_dict = {
            "record_number": enum,
            "messages": thread_messages,
            "file_name": file_name,
            **{k: v for k, v in item.items() if k != "thread"}
        }
        return DuckieThread.from_dict(thread_dict)

class DocLoader(ContentLoader):
    def load(self, file_path: str) -> List[DuckieDoc]:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        file_name = self._get_file_name(file_path)
        return [DuckieDoc.from_dict({**item, 'record_number': enum, 'file_name': file_name}) 
                for enum, item in enumerate(data)]

class TicketLoader(ContentLoader):
    def load(self, file_path: str) -> List[DuckieTicket]:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        tickets = []
        file_name = self._get_file_name(file_path)
        
        for enum, item in enumerate(data):
            comments = self._create_comments(item["comments"])
            ticket = self._create_ticket(item, enum, file_name, comments)
            tickets.append(ticket)
        
        return tickets

    def _create_comments(self, comments_data: List[Dict[str, Any]]) -> List[DuckieTicketComment]:
        return [DuckieTicketComment.from_dict(CommentExtractor.extract_comment_info(comment)) 
                for comment in comments_data]

    def _create_ticket(self, item: Dict[str, Any], enum: int, file_name: str, comments: List[DuckieTicketComment]) -> DuckieTicket:
        ticket_dict = {
            "record_number": enum,
            "user": item['reporter'],
            "comments": comments,
            "file_name": file_name,
            "timestamp": datetime.strptime(item["timestamp"], "%Y-%m-%dT%H:%M:%S.%f%z"),
            **{k: v for k, v in item.items() if k not in ["state", "reporter", "comments", "timestamp"]}
        }
        return DuckieTicket.from_dict(ticket_dict)
