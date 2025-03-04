import asyncio
from src.llm.completion import *
from src.llm.completion.openrouter_completion import OpenRouterCompletion
from src.llm.dtypes import CompletionArgs, ModelName, ModelProvider

def generate_llm_response(
    messages: list[dict],
    provider: ModelProvider,
    model: ModelName,
    max_tokens: int = 4096,
    temperature: float = 0,
    json_mode: bool = False
) -> str:
    return asyncio.run(generate_llm_response_async(messages, provider, model, max_tokens, temperature, json_mode))

async def generate_llm_response_async(
    messages: list[dict],
    provider: ModelProvider,
    model: ModelName,
    max_tokens: int = 4096,
    temperature: float = 0,
    json_mode: bool = False
) -> str:
    args = CompletionArgs(
        messages=messages,
        provider=provider,
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
        json_mode=json_mode
    )
    if args.provider == ModelProvider.OPENAI:
        return await OpenAiCompletion(args).generate_response()
    elif args.provider == ModelProvider.ANTHROPIC:
        return await AnthropicCompletion(args).generate_response()
    elif args.provider == ModelProvider.OPENROUTER:
        return await OpenRouterCompletion(args).generate_response()
    else:
        raise ValueError(f"Unsupported provider: {args.provider}")

if __name__ == "__main__":
    messages=[{"role": "user", "content": "Hello, world!"}]
    provider=ModelProvider.OPENROUTER
    model=ModelName.MISTRAL_8B
    json_mode=False

    resp = asyncio.run(generate_llm_response_async(messages, provider, model, json_mode=json_mode))
    print(resp)