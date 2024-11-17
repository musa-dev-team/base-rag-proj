from typing import Any, Dict, List, Union
from datetime import datetime 

class CommentExtractor:
    @staticmethod
    def extract_comment_info(comment: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'comment_id': comment.get('id'),
            'content': CommentExtractor._extract_text(comment),
            'timestamp': CommentExtractor._parse_timestamp(comment.get('created')),
            'user': comment.get('author', {}).get('displayName')
        }

    @staticmethod
    def _extract_text(comment: Dict[str, Any]) -> str:
        body = comment.get('body', {})
        if isinstance(body, dict) and 'content' in body:
            return CommentExtractor._extract_text_from_content(body['content'])
        return comment.get('renderedBody') or body

    @staticmethod
    def _extract_text_from_content(content: List[Dict[str, Any]]) -> str:
        text_parts = []
        for item in content:
            if item['type'] == 'paragraph':
                for para_content in item.get('content', []):
                    if para_content['type'] == 'text':
                        text_parts.append(para_content['text'])
        return ' '.join(text_parts)

    @staticmethod
    def _parse_timestamp(timestamp_str: str) -> Union[datetime, None]:
        try:
            return datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%S.%f%z")
        except (ValueError, TypeError):
            return None