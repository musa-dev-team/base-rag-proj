from dotenv import load_dotenv

load_dotenv()

import logging
import ollama

from src.llm.llm_completion import LLMCompletion


class OllamaCompletion(LLMCompletion):
    def generate_text(self, **kwargs) -> str:
        logging.info(f"Ollama: Generating text")

        args = kwargs
        args["model"] = "llama3" if not args.get("model") else args.get("model")
        response = ollama.chat(**args)

        logging.info(f"Ollama: Finished generating text")
        return response["message"]["content"]
