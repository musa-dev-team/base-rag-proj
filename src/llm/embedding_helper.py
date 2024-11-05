from dotenv import load_dotenv

load_dotenv()

import os
import openai

def generate_embedding(text, model="text-embedding-3-small"):
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    return client.embeddings.create(input=[text], model=model).data[0].embedding