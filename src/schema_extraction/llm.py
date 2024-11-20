import logging
import logging
from langchain.docstore.document import Document
import os
from langchain_openai import ChatOpenAI

def get_llm(model_name: str):
    """Retrieve the specified language model based on the model name."""
    env_key = "OPENAI_API_KEY"
    env_value = os.environ.get(env_key)
    logging.info("Model: {}".format(env_key))
    
    api_key = env_value
    llm = ChatOpenAI(
        api_key=api_key,
        model=model_name,
        temperature=0,
    )


    logging.info(f"Model created - Model Version: {model_name}")
    return llm, model_name
