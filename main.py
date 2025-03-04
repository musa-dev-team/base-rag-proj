from src.llm.dtypes import ModelName, ModelProvider
from src.llm.generate import generate_llm_response


if __name__ == "__main__":
    test_messages = [
        {"role": "user", "content": "Hello, how are you?"}
    ]

    response = generate_llm_response(test_messages, provider=ModelProvider.OPENAI, model=ModelName.GPT_4O)

    print(response)