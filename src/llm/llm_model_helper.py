import copy
import re
from dotenv import load_dotenv
from src.llm.llm_model import LLMModel, ModelPreference, ModelType
from src.llm.tools.tool import Tool

load_dotenv()

def get_model(
    model_type: ModelType, model: LLMModel = None
) -> LLMModel:
    if model is not None:
        return model

    model_preference = ModelPreference.get(model_type)
    if model_preference is None:
        raise Exception(f"No model preference found for {model_type}")
    
    return model_preference[0]

def clean_json_string(json_string):
    pattern = r"^```json\s*(.*?)\s*```$"
    cleaned_string = re.sub(pattern, r"\1", json_string, flags=re.DOTALL)
    return cleaned_string.strip()

def generate_llm_response(
    messages: list,
    model_type: ModelType = None,
    model: LLMModel = None,
    temperature: float = 0,
    response_format: str = None,
    tool: Tool = None,
    max_tokens: int = 4096,
) -> str:
    if model_type is None and model is None:
        raise Exception("Either model_type or model must be provided")

    messages = copy.deepcopy(messages)
    model = get_model(model_type, model)

    response = model.generate(
        messages, temperature, response_format, tool, max_tokens
    )
    
    return clean_json_string(response)
