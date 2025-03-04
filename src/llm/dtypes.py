from enum import Enum
import os


class ModelProvider(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    BEDROCK = "bedrock"
    AZURE = "azure"
    OPENROUTER = "openrouter"

class ModelName(Enum):
    GPT_4O_MINI = "gpt-4o-mini"
    GPT_4O = "gpt-4o"
    GPT_O1 = "o1-preview"
    GPT_O1_MINI = "o1-mini"
    GPT_O3_MINI = "o3-mini"
    CLAUDE_3_5_SONNET = "claude-3-5-sonnet-20240620"
    CLAUDE_3_7_SONNET = "claude-3-7-sonnet-20250219"
    MISTRAL_8B = "mistralai/ministral-8b"
    LLAMA_3_2_1B = "meta-llama/llama-3.2-3b-instruct"

class CompletionArgs:
    messages: list[dict]
    provider: ModelProvider
    model: ModelName
    max_tokens: int = 4096
    temperature: float = 0
    json_mode: bool = False

    def __init__(self, messages: list[dict], provider: ModelProvider, model: ModelName, max_tokens: int = None, temperature: float = None, json_mode: bool = False):
        self.messages = messages
        self.provider = provider
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.json_mode = json_mode

    @property
    def api_key(self):
        if self.provider == ModelProvider.OPENAI:
            return os.getenv("OPENAI_API_KEY")
        elif self.provider == ModelProvider.ANTHROPIC:
            return os.getenv("ANTHROPIC_API_KEY")
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    def validate_args(self):
        if self.provider == ModelProvider.OPENAI:
            if self.model not in [ModelName.GPT_4O_MINI, ModelName.GPT_4O, ModelName.GPT_O1_MINI, ModelName.GPT_O1, ModelName.GPT_O3_MINI]:
                raise ValueError(f"Invalid model {self.model} for OpenAI provider")
        elif self.provider == ModelProvider.ANTHROPIC:
            if self.model not in [ModelName.CLAUDE_3_5_SONNET, ModelName.CLAUDE_3_7_SONNET]:
                raise ValueError(f"Invalid model {self.model} for Anthropic provider")
        elif self.provider == ModelProvider.OPENROUTER:
            if self.model not in [ModelName.MISTRAL_8B, ModelName.LLAMA_3_2_1B]:
                raise ValueError(f"Invalid model {self.model} for OpenRouter provider")
        else:
            raise ValueError(f"Invalid provider {self.provider}")