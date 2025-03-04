import json
import logging
from dotenv import load_dotenv
import httpx

from src.duckie_logging.duckie_logger import logging
from src.llm.completion.base_completion import LLMCompletion
from src.llm.dtypes import CompletionArgs

load_dotenv(override=True)


class AnthropicCompletion(LLMCompletion):
    def __init__(self, args: CompletionArgs):
        super().__init__(args)
        self.system_message = None

    async def _generate_response(self) -> str:
        self._prepare_messages()
        response = await self._create_message()

        if response.status_code != 200:
            raise Exception(f"Anthropic API error: {response.text}")

        response = response.json()
        return response["content"][0]["text"]

    async def _create_message(self) -> httpx.Response:
        if self.system_message is None:
            raise ValueError("System message is required")

        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": self.args.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        data = {
            "model": self.args.model.value,
            "temperature": self.args.temperature,
            "max_tokens": self.args.max_tokens,
            "messages": self.args.messages,
            "system": self.system_message
        }
        try:
            async with httpx.AsyncClient(timeout=90) as client:
                response = await client.post(url, headers=headers, json=data)
                return response

        except Exception as e:
            exception_message = f"Anthropic API request failed with error: {e}\nHeaders: {json.dumps(headers)}\nData: {json.dumps(data)}"
            logging.error(exception_message)
            raise Exception(exception_message)

    def _is_messages_payload(self):
        return len(self.args.messages) > 1 or (
            len(self.args.messages) == 1 and self.args.messages[0]["role"] != "system"
        )

    def _prepare_messages(self):
        messages = self.args.messages
        self.system_message = next(
            (msg["content"] for msg in messages if msg["role"] == "system"), None
        )
        if self.system_message is None:
            self.args.messages[0]["role"] = "system"
            self.system_message = self.args.messages[0]["content"]

        self.args.messages = [msg for msg in self.args.messages if msg["role"] != "system"]

        if len(self.args.messages) == 0:
            self.args.messages = [{"role": "user", "content": self.system_message}]


    def _parse_function_response(self, response):
        for content in response["content"]:
            if content["type"] == "tool_use" and "name" in content:
                return json.dumps(content["input"], indent=2)

        return json.dumps(
            {"message": "No function call detected in response."}, indent=2
        )

    @staticmethod
    def get_vision_messages(image_data: list):
        images_content = []
        for i, data in enumerate(image_data):
            images_content += [
                {"type": "text", "text": f"Image {i+1}"},
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": data["media_type"],
                        "data": data["data"].split(",")[1],
                    },
                },
            ]
        return [{"role": "user", "content": images_content}]
