
from src.llm.generate import generate_llm_response
from src.llm.dtypes import ModelName, ModelProvider

def test_generate_llm_response():
    test_messages = [
        {"role": "user", "content": "Hello, how are you?"}
    ]

    response = generate_llm_response(test_messages, provider=ModelProvider.OPENAI, model=ModelName.GPT_4O)
    
    assert response is not None
