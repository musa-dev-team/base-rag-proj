import os
from abc import abstractmethod
from dataclasses import dataclass
from dotenv import load_dotenv

from src.llm.anthropic_completion import AnthropicCompletion
from src.llm.llm_completion import LLMCompletion
from src.llm.openai_completion import OpenAiCompletion
from src.llm.tools.tool import Tool

load_dotenv()

class ModelProvider:
    OPENAI = "openai"
    ANTHROPIC = "anthropic"

    @staticmethod
    def get_all_models(model_provider: "ModelProvider") -> list["LLMModel"]:
        models = []
        for model in ModelPreference.get(ModelType.ALL_LLM):
            if model.model_provider == model_provider:
                models.append(model)
        return models


class ProviderCompletion:
    mapping = {
        ModelProvider.OPENAI: OpenAiCompletion(),
        ModelProvider.ANTHROPIC: AnthropicCompletion(),
    }

    @staticmethod
    def get_all_models(model_provider: ModelProvider):
        return ProviderCompletion.mapping.get(model_provider)


class ModelType:
    LARGE = "large"
    SMALL = "small"
    RESPONSE_LARGE = "response_large"
    RESPONSE_SMALL = "response_small"
    REASONING_LARGE = "reasoning_large"
    REASONING_SMALL = "reasoning_small"
    IMAGE = "image"
    EMBEDDING = "embedding"
    ALL_LLM = "all"


@dataclass
class LLMModel:
    model_provider: ModelProvider
    model_name: str

    @classmethod
    def get_model(cls, model_provider: ModelProvider, model_name: str) -> "LLMModel":
        all_models = ModelPreference.get(ModelType.ALL_LLM)
        for model in all_models:
            if model.model_name == model_name and model.model_provider == model_provider:
                return model
        raise Exception(f"Model not found: {model_provider} {model_name}")

    def get_vision_messages(self, image_data: list) -> list[dict]:
        return self.get_completion().get_vision_messages(image_data)

    @abstractmethod
    def format_messages_kwargs(self, messages: list): ...

    @abstractmethod
    def format_tool_kwargs(self, tool: Tool): ...

    @abstractmethod
    def format_base_kwargs(self, temperature, response_format, max_tokens): ...

    @abstractmethod
    def format_api_kwargs(self):
        if self.model_provider == ModelProvider.OPENAI:
            return {"api_key": os.getenv("OPENAI_API_KEY")}
        elif self.model_provider == ModelProvider.ANTHROPIC:
            return {"api_key": os.getenv("ANTHROPIC_API_KEY")}

        raise Exception(f"No model provider found for {self.model_provider}")

    def format_kwargs(
        self,
        messages: list,
        temperature: float,
        response_format: str,
        tool: Tool,
        max_tokens: int,
    ):
        kwargs = {}
        base_kwargs = self.format_base_kwargs(temperature, response_format, max_tokens)
        messages_kwargs = self.format_messages_kwargs(messages)
        api_kwargs = self.format_api_kwargs()
        tool_kwargs = self.format_tool_kwargs(tool)

        kwargs.update(base_kwargs)
        kwargs.update(messages_kwargs)
        kwargs.update(api_kwargs)
        if tool_kwargs is not None:
            kwargs.update(tool_kwargs)

        return kwargs

    def get_completion(self) -> LLMCompletion:
        return ProviderCompletion.get_all_models(self.model_provider)

    def generate(
        self,
        messages: list,
        temperature: float = 0,
        response_format: str = None,
        tool: Tool = None,
        max_tokens: int = 4096,
    ):
        kwargs = self.format_kwargs(
            messages, temperature, response_format, tool, max_tokens
        )
        return self.get_completion().generate_text(**kwargs)


@dataclass
class GptModel(LLMModel):
    model_provider: ModelProvider = None
    model_name: str = None

    def format_messages_kwargs(self, messages: list):
        # Ensure the system message is the first message
        for i, message in enumerate(messages):
            if message["role"] == "system" and i > 0:
                # Move the system message to the first position
                messages.insert(0, messages.pop(i))
                break
        return {"messages": messages}

    def format_tool_kwargs(self, tool_class: Tool):
        if tool_class is None:
            return None

        if self.model_provider == ModelProvider.OPENAI:
            tool_class.tools = {
                name: tool_class.openai_transform(tool)
                for name, tool in tool_class.tools.items()
            }
            return {
                "functions": [tool_class.get_tool_schema()],
                "function_call": {"name": tool_class.name},
            }
        else:
            raise ValueError(f"Model not supported")

    def format_base_kwargs(self, temperature, response_format, max_tokens):
        kwargs = {
            "model": self.model_name,
            "temperature": temperature,
            "response_format": response_format,
            "max_tokens": max_tokens,
        }
        return kwargs


@dataclass
class O1Model(LLMModel):
    def format_messages_kwargs(self, messages: list):
        # There can only be assistant and user messages
        for message in messages:
            if message["role"] == "system":
                message["role"] = "assistant"
        return {"messages": messages}

    def format_tool_kwargs(self, tool_class: Tool):
        return None

    def format_base_kwargs(self, temperature, response_format, max_tokens):
        return {"model": self.model_name}


@dataclass
class ClaudeModel(LLMModel):
    def format_messages_kwargs(self, messages: list):
        """
        Rules:
        - There must be a system message at the start
        - There must be a user message after every assistant message
        - The last message must be a user message
        - There must be at least one user message
        - Roles must follow: system, user, (assistant, user)*
        - If the first message is an assistant message, make the first message the system message
        - If the first message is a user message, create a system message with content "."
        """
        if not messages:
            raise Exception("Messages cannot be empty")

        # First, deduplicate consecutive messages from the same role
        deduped_messages = []
        for message in messages:
            if deduped_messages and deduped_messages[-1]["role"] == message["role"]:
                deduped_messages[-1]["content"] += message["content"]
            else:
                deduped_messages.append(message)
        messages = deduped_messages

        # Ensure there is no system message after the first message
        for i in range(1, len(messages)):
            if messages[i]["role"] == "system":
                raise Exception("System message must be the first message")

        # Ensure there's a system message at the start
        if messages[0]["role"] == "system":
            pass
        elif messages[0]["role"] == "assistant":
            messages[0]["role"] = "system"
        else:
            messages.insert(0, {"role": "system", "content": "."})

        # Ensure the first message is a user message
        if len(messages) == 1:
            messages.append({"role": "user", "content": "."})
        if messages[1]["role"] == "assistant":
            messages.insert(1, {"role": "user", "content": "."})

        # Ensure the last message is a user message
        if messages[-1]["role"] != "user":
            messages.append({"role": "user", "content": "."})

        # Ensure a user message follows every assistant message
        for i in range(len(messages)):
            if messages[i]["role"] == "assistant":
                if i + 1 >= len(messages) or messages[i + 1]["role"] != "user":
                    messages.insert(i + 1, {"role": "user", "content": "."})

        return {"messages": messages}

    def format_base_kwargs(self, temperature, response_format, max_tokens):
        return {
            "model": self.model_name,
            "temperature": temperature,
            "response_format": response_format,
            "max_tokens": max_tokens,
        }

@dataclass
class OpenAiGpt4o(GptModel):
    model_provider: ModelProvider = ModelProvider.OPENAI
    model_name: str = "gpt-4o"


@dataclass
class OpenAiGpt4oMini(GptModel):
    model_provider: ModelProvider = ModelProvider.OPENAI
    model_name: str = "gpt-4o-mini"


@dataclass
class OpenAiO1(O1Model):
    model_provider: ModelProvider = ModelProvider.OPENAI
    model_name: str = "o1-preview"


@dataclass
class OpenAiO1Mini(O1Model):
    model_provider: ModelProvider = ModelProvider.OPENAI
    model_name: str = "o1-mini"


@dataclass
class AnthropicClaude35Sonnet(ClaudeModel):
    model_provider: ModelProvider = ModelProvider.ANTHROPIC
    model_name: str = "claude-3-5-sonnet-20240620"

    def format_tool_kwargs(self, tool_class: Tool):
        if tool_class is None:
            return None

        tool_class.tools = {
            name: tool_class.anthropic_transform(tool)
            for name, tool in tool_class.tools.items()
        }
        return {
            "tools": [tool_class.get_tool_schema()],
            "toolChoice": {"type": "tool", "name": tool_class.name},
        }

@dataclass
class OpenAiTextEmbeddingsSmall(LLMModel):
    model_provider: ModelProvider = ModelProvider.OPENAI
    model_name: str = "text-embedding-3-small"


class ModelPreference:
    mapping: dict[ModelType, list[LLMModel]] = {
        ModelType.LARGE: [
            OpenAiGpt4o(),
            OpenAiGpt4oMini(),
            AnthropicClaude35Sonnet(),
            OpenAiO1(),
            OpenAiO1Mini(),
        ],
        ModelType.SMALL: [
            OpenAiGpt4oMini(),
            OpenAiGpt4o(),
            AnthropicClaude35Sonnet(),
            OpenAiO1(),
            OpenAiO1Mini(),
        ],
        ModelType.RESPONSE_LARGE: [
            AnthropicClaude35Sonnet(),
            OpenAiGpt4o(),
            OpenAiGpt4oMini(),
            OpenAiO1(),
            OpenAiO1Mini(),
        ],
        ModelType.RESPONSE_SMALL: [
            OpenAiGpt4oMini(),
            OpenAiO1Mini(),
            AnthropicClaude35Sonnet(),
            OpenAiGpt4o(),
            OpenAiO1(),
        ],
        ModelType.REASONING_LARGE: [
            OpenAiO1(),
            OpenAiO1Mini(),
            OpenAiGpt4o(),
            AnthropicClaude35Sonnet(),
            OpenAiGpt4oMini(),
        ],
        ModelType.REASONING_SMALL: [
            OpenAiO1Mini(),
            OpenAiO1(),
            OpenAiGpt4oMini(),
            AnthropicClaude35Sonnet(),
            OpenAiGpt4o(),
        ],
        ModelType.IMAGE: [
            OpenAiGpt4oMini(),
            OpenAiGpt4o(),
            AnthropicClaude35Sonnet(),
        ],
        ModelType.EMBEDDING: [OpenAiTextEmbeddingsSmall()],
        ModelType.ALL_LLM: [
            OpenAiGpt4o(),
            OpenAiGpt4oMini(),
            AnthropicClaude35Sonnet(),
            OpenAiO1(),
            OpenAiO1Mini(),
        ],
    }

    @staticmethod
    def get(model_type: ModelType) -> list[LLMModel]:
        return ModelPreference.mapping.get(model_type, [])
