import asyncio
import json
import logging
import os
import httpx

from src.duckie_logging.duckie_logger import logging
from src.llm.completion.base_completion import LLMCompletion
from src.llm.dtypes import ModelName

class OpenAiCompletion(LLMCompletion):
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
            response = await OpenAiCompletion._chat_completion_api(oargs)
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
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
            "Content-Type": "application/json",
        }
        async with httpx.AsyncClient(timeout=90) as client:
            response = await client.post(url, headers=headers, json=data)
        response = response.json()
        if 'error' in response:
            raise Exception(response["error"]["message"])
        return response

    @staticmethod
    def is_rate_limited(e: Exception) -> bool:
        return "too many requests" in str(e).lower()

    @staticmethod
    async def get_embedding(text: str):
        backoff = 1
        while backoff < 30:
            try:
                response = await OpenAiCompletion.call_embedding_api(text)
                return response["data"][0]["embedding"]
            except Exception as e:
                if OpenAiCompletion.is_rate_limited(e):
                    logging.warning(f"OpenAiCompletion: Too many requests, backing off for {backoff} seconds")
                    await asyncio.sleep(backoff)
                    backoff *= 2
                else:
                    raise e
        raise Exception("Failed to get embedding")
    
    @staticmethod
    async def call_embedding_api(text: str):
        url = "https://api.openai.com/v1/embeddings"
        headers = {
            "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
            "Content-Type": "application/json",
        }
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post(url, headers=headers, json={"input": text, "model": "text-embedding-3-small"})
        response = response.json()
        if 'error' in response:
            raise Exception(response["error"]["message"])
        return response
    
    def _clean_oargs(self, oargs: dict) -> dict:
        if self.args.model in [ModelName.GPT_O1_MINI, ModelName.GPT_O1, ModelName.GPT_O3_MINI]:
            oargs.pop("max_tokens", None)
            oargs.pop("temperature", None)
            oargs.pop("response_format", None)

            if "system" in [msg["role"] for msg in oargs["messages"]]:
                logging.warning("System messages are not supported for reasoning models. Converting to user messages.")

            for msg in oargs["messages"]:
                if msg["role"] == "system":
                    msg["role"] = "user"

        return oargs

if __name__ == "__main__":
    # resp = asyncio.run(OpenAiCompletion._chat_completion_api({
    #     "messages": [{"role": "user", "content": "Hello, how are you?"}],
    #     "model": "gpt-4o-mini",
    #     "max_tokens": 4096,
    #     "temperature": 0
    # }))
    # print(resp)

    resp = asyncio.run(OpenAiCompletion.get_embedding("Hello, how are you?"))
    print(resp)