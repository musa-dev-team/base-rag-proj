import asyncio
import json
import logging
import os
import httpx

from src.duckie_logging.duckie_logger import logging
from src.llm.completion.base_completion import LLMCompletion
from src.llm.dtypes import ModelName

class OpenRouterCompletion(LLMCompletion):
    async def _generate_response(self) -> str:
        oargs = {
            "messages": self.args.messages,
            "model": self.args.model.value,
            "max_tokens": self.args.max_tokens,
            "temperature": self.args.temperature,
        }

        if self.args.json_mode:
            oargs["response_format"] = {"type": "json_object"}

        oargs = self._clean_oargs(oargs)

        try:
            response = await OpenRouterCompletion._chat_completion_api(oargs)
            return response["choices"][0]["message"]["content"]
        except Exception as e:
            logging.error(f"OpenAiCompletion: Error during API call: {str(e)}")
            logging.error(
                f"OpenAiCompletion: Args at time of error: {json.dumps(dict(oargs))}"
            )
            raise

    @staticmethod
    def get_vision_messages(image_data: list) -> str:
        image_data_urls = [
            {"type": "image_url", "image_url": {"url": data["data"]}}
            for data in image_data
        ]
        return [{"role": "user", "content": [*image_data_urls]}]
    
    @staticmethod
    async def _chat_completion_api(data: dict) -> str:
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
            "Content-Type": "application/json",
        }
        data["base_url"] = "https://openrouter.ai/api/v1"
        async with httpx.AsyncClient(timeout=90) as client:
            response = await client.post(url, headers=headers, json=data)
        response = response.json()
        if 'error' in response:
            raise Exception(response["error"]["message"])
        return response

    @staticmethod
    def is_rate_limited(e: Exception) -> bool:
        return "too many requests" in str(e).lower()
    
    def _clean_oargs(self, oargs: dict) -> dict:
        if self.args.model in [ModelName.GPT_O1_MINI, ModelName.GPT_O1, ModelName.GPT_O3_MINI]:
            oargs.pop("max_tokens", None)
            oargs.pop("temperature", None)
            oargs.pop("response_format", None)

            if "system" in [msg["role"] for msg in oargs["messages"]]:
                raise Exception("System messages are not supported for reasoning models")

        return oargs

if __name__ == "__main__":

    resp = asyncio.run(OpenRouterCompletion._chat_completion_api({
        "messages": [{"role": "user", "content": "Hello, how are you?"}],
        "model": "mistralai/ministral-8b",
        "max_tokens": 4096,
        "temperature": 0
    }))
    print(resp)