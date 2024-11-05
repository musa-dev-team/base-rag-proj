import json
import logging
import openai
from frozendict import frozendict

from src.llm.llm_completion import LLMCompletion
from contextlib import contextmanager


class OpenAiCompletion(LLMCompletion):
    def generate_text(self, **kwargs) -> str:
        from src.utils.utils import rate_limit_function

        generate_text_decorated = rate_limit_function(self._generate_text_impl)
        return generate_text_decorated(**kwargs)

    def _generate_text_impl(self, **kwargs) -> str:
        logging.debug(
            f"OpenAiCompletion: Generating text with kwargs: {json.dumps(kwargs)}"
        )

        api_key = kwargs.pop("api_key", None)
        if not api_key:
            raise ValueError("Missing required argument: api_key")

        args = kwargs

        if "functions" in kwargs and kwargs["functions"] is not None:
            args["functions"] = tuple(frozendict(func) for func in kwargs["functions"])

        if "response_format" in kwargs and kwargs["response_format"] is not None:
            args["response_format"] = frozendict(kwargs["response_format"])

        if "function_call" in kwargs and kwargs["function_call"] is not None:
            args["function_call"] = frozendict(kwargs["function_call"])

        args = frozendict(args)

        logging.debug(f"OpenAiCompletion: Prepared args: {json.dumps(dict(args))}")

        try:
            with self._get_client(kwargs.get("api_key")) as client:
                logging.debug(
                    f"OpenAiCompletion: About to call API with args: {json.dumps(dict(args))}"
                )
                response = client.chat.completions.create(**dict(args))
                logging.debug(f"OpenAiCompletion: API call successful")
        except Exception as e:
            logging.error(f"OpenAiCompletion: Error during API call: {str(e)}")
            logging.error(
                f"OpenAiCompletion: Args at time of error: {json.dumps(dict(args))}"
            )
            raise

        logging.debug(f"OpenAiCompletion: Finished generating text")
        if "functions" in args:
            resp = self._parse_function_response(response)
        else:
            resp = response.choices[0].message.content

        return resp

    def _parse_function_response(self, response):
        function_call = response.choices[0].message.function_call

        if function_call:
            json_data = json.loads(function_call.arguments)
            return json.dumps(json_data, indent=2)

        elif response.content:
            return {
                "function_name": "non_function_response",
                "function_args": {"message": response.content},
            }

    @contextmanager
    def _get_client(self, api_key: str = None):
        client = openai.OpenAI(api_key=api_key)
        try:
            yield client
        finally:
            client.close()

    def get_vision_messages(self, image_data: list) -> str:
        image_data_urls = [
            {"type": "image_url", "image_url": {"url": data["data"]}}
            for data in image_data
        ]
        return [{"role": "user", "content": [*image_data_urls]}]
