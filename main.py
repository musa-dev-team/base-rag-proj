from src.llm.llm_model import ModelType
from src.llm.llm_model_helper import generate_llm_response

if __name__ == "__main__":
    test_messages = [
        {"role": "user", "content": "Hello, how are you?"}
    ]

    response = generate_llm_response(test_messages, model_type=ModelType.SMALL)

    print(response)