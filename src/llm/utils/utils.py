
import asyncio
from src.llm.completion.anthropic_completion import AnthropicCompletion
from src.llm.completion.openai_completion import OpenAiCompletion
from src.llm.dtypes import ModelName, ModelProvider
from src.llm.generate import generate_llm_response_async
from src.llm.utils.prompts import IMAGE_DESCRIPTION_PROMPT_SYSTEM_PROMPT
from src.utils.utils import file_to_image_data


def text_to_messages(text: str, role: str = "user"):
    return [{"role": role, "content": text}]

async def describe_image_message(
    provider: ModelProvider,
    model: ModelName,
    dl_files: list, 
    message_text: str = "Here's the image"
):
    image_data_base64 = [
        file_to_image_data(file["content"], file["mimetype"]) for file in dl_files
    ]

    image_data = []
    for i in range(len(image_data_base64)):
        image_data.append(
            {"media_type": dl_files[i]["mimetype"], "data": image_data_base64[i]}
        )

    system_message = [
        {
            "role": "system",
            "content": IMAGE_DESCRIPTION_PROMPT_SYSTEM_PROMPT.replace("{user_message}", message_text)
        }
    ]
    vision_messages = format_vision_message(
        image_data, provider
    )
    messages = system_message + vision_messages

    return await generate_llm_response_async(
        messages,
        provider,
        model,
        max_tokens=350
    )

def format_vision_message(
    image_data: list,
    provider: ModelProvider,
):
    if provider == ModelProvider.OPENAI:
        return OpenAiCompletion.get_vision_messages(image_data)
    elif provider == ModelProvider.ANTHROPIC:
        return AnthropicCompletion.get_vision_messages(image_data)
    else:
        raise ValueError(f"Unsupported provider: {provider}")
    

def get_embedding(text: str):
    return asyncio.run(get_embedding_async(text))

async def get_embedding_async(text: str):
    return await OpenAiCompletion.get_embedding(text)
