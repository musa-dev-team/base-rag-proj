import json
import logging
import os
from dotenv import load_dotenv
import requests

from src.llm.llm_completion import LLMCompletion
from src.utils.utils import rate_limit_function


load_dotenv(override=True)


class AnthropicCompletion(LLMCompletion):
    def generate_text(self, **kwargs) -> str:
        from src.utils.utils import rate_limit_function

        messages = kwargs.get("messages", [])

        if self._is_messages_payload(messages):
            args = self._prepare_messages_payload_args(kwargs)
        else:
            args = self._prepare_prompt_template_args(kwargs)
        response = self.create_message(args)

        if response.status_code != 200:
            raise Exception(f"Anthropic API error: {response.error}")
        response = response.json()

        if "tools" in args:
            resp = self._parse_function_response(response)
        else:
            resp = response["content"][0]["text"]

        return resp

    def create_message(self, kwargs):
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": kwargs.get("api_key"),
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        data = kwargs.copy()
        data.pop("api_key", None)
        try:
            return rate_limit_function(requests.post)(
                url, headers=headers, data=json.dumps(data)
            )
        except Exception as e:
            exception_message = f"Anthropic API request failed with error: {e}\nHeaders: {json.dumps(headers)}\nData: {json.dumps(data)}"
            logging.error(exception_message)
            raise Exception(exception_message)

    def _is_messages_payload(self, messages):
        return len(messages) > 1 or (
            len(messages) == 1 and messages[0]["role"] != "system"
        )

    def _prepare_messages_payload_args(self, kwargs):
        messages = kwargs.get("messages", [])
        system_message = next(
            (msg["content"] for msg in messages if msg["role"] == "system"), None
        )
        messages = [msg for msg in messages if msg["role"] != "system"]

        args = {
            "model": kwargs.get("model", os.getenv("ANTHROPIC_DEFAULT_MODEL")),
            "temperature": kwargs.get("temperature", 0),
            "max_tokens": kwargs.get("max_tokens", 4096),
            "messages": messages,
            "system": system_message,
            "api_key": kwargs.get("api_key"),
        }

        if "tools" in kwargs and kwargs["tools"] is not None:
            args["tools"] = kwargs["tools"]

        if "tool_choice" in kwargs and kwargs["tool_choice"] is not None:
            args["tool_choice"] = kwargs["tool_choice"]

        return args

    def _prepare_prompt_template_args(self, kwargs):
        messages = kwargs.get("messages", [])
        system_message = next(
            (msg["content"] for msg in messages if msg["role"] == "system"), None
        )

        args = {
            "model": kwargs.get("model", os.getenv("ANTHROPIC_DEFAULT_MODEL")),
            "temperature": kwargs.get("temperature", 0),
            "max_tokens": kwargs.get("max_tokens", 4096),
            "messages": [{"role": "user", "content": "Complete your action."}],
            "system": system_message,
            "api_key": kwargs.get("api_key"),
        }

        if "tools" in kwargs and kwargs["tools"] is not None:
            args["tools"] = kwargs["tools"]

        if "tool_choice" in kwargs and kwargs["tool_choice"] is not None:
            args["tool_choice"] = kwargs["tool_choice"]

        return args

    def _parse_function_response(self, response):
        for content in response["content"]:
            if content["type"] == "tool_use" and "name" in content:
                return json.dumps(content["input"], indent=2)

        return json.dumps(
            {"message": "No function call detected in response."}, indent=2
        )

    def get_vision_messages(self, image_data: list):
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
