from src.llm.llm_model import ModelType
from src.llm.llm_model_helper import generate_llm_response
from src.supabase_helper import get_supabase

def test_generate_llm_response():
    test_messages = [
        {"role": "user", "content": "Hello, how are you?"}
    ]

    response = generate_llm_response(test_messages, model_type=ModelType.SMALL)
    
    assert response is not None

def test_read_from_supabase():
    supabase = get_supabase()
    data = supabase.table("users").select("*").execute().data
    print(data)
    assert data is not None
    assert len(data) > 0