# Project: Duckie RAG System

## Project Structure

Below is a brief overview of the project structure:

### Data

- **/data**
  - **/data/raw**: Contains raw data files for processing and ingestion.

### Logic

1. **Data Ingestion (src/ingestion/)**:
   - Skeleton code for ingesting data.

2. **Retrieval (src/retrieval/)**:
   - Skeleton code for retrieval.

3. **LLM Integration (src/llm/)**:
   - Logic to abstract away the LLM provider.
   - Support for OpenAI, Anthropic, and OpenRouter models.
   - Model definitions and classes dedicated to handling text generation.

4. **Data Classes (src/duckie_objects/)**:
   - Entity objects related to threads, documentation, and ticket management.

5. **Utilities (src/utils/)**:
   - Functions for utilities such as rate limiting, content conversion, and tokenization.

6. **Vector Database (src/vector_db/)**:
   - Manages interactions with a Chroma vector database, facilitating embedding storage and retrieval.

## Getting Started
1. Install the dependencies using `pip install -r requirements.txt`
2. Familiarize yourself with the existing data and source structure.
3. Focus on the ingestion and retrieval components.

## Expectations
- **Code Quality**: Maintain clean, concise, and modular code.
- **Test Driven Development**: Use the synthetic QA data to evaluate the accuracy of the retrieval and ingestion components, and to iteratively improve the system.
- **Communication**: Treat the project as if you were a part of the Duckie team. We believe in open communication and collaboration, so don't hesitate to ask questions or bring up ideas!
