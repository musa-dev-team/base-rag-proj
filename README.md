# Project: Duckie RAG System

## Overview

Welcome to the Duckie trial project! Your task is to implement an ingestion and retrieval system for a RAG project.

## Project Structure

Below is a brief overview of the project structure and where your focus will be:

### Data

- **/data**
  - **/data/raw**: Contains raw data files for processing and ingestion.
  - **/data/synthetic_qa**: Contains synthetic QA data for testing system functionality.

### Logic

1. **Data Ingestion (src/ingestion/)**:
   - Skeleton code for ingesting data.

2. **Retrieval (src/retrieval/)**:
   - Skeleton code for retrieval.

3. **LLM Integration (src/llm/)**:
   - Logic to abstract away the LLM provider.
   - Support for OpenAI, Anthropic, and Ollama models.
   - Model definitions and classes dedicated to handling text generation.
   - Additional helper functions for model preference settings and response generation.

4. **Data Classes (src/duckie_objects/)**:
   - Entity objects related to threads, documentation, and ticket management.

5. **Utilities (src/utils/)**:
   - Functions for utilities such as rate limiting, content conversion, and tokenization.

6. **Vector Database (src/weaviate_db/)**:
   - Manages interactions with a Weaviate vector database, facilitating embedding storage and retrieval.

7. **Postgres Database (src/supabase_helper/)**:
   - Manages interactions with a Supabase postgres database, used for storing non-vector data.

## Objective

Your goal is to complete the implementation of the ingestion and retrieval components. The ingestion component should be capable of processing raw data and storing the relevant information within a Weaviate vector database and (optionally) a Postgres database. The retrieval component should take a query and return the relevant data from the database.

## Getting Started
1. Install the dependencies using `pip install -r requirements.txt`
2. Familiarize yourself with the existing data and source structure.
3. Focus on the ingestion and retrieval components.
4. Use the synthetic QA data for evaluation of your implementation.

## Expectations
- **Code Quality**: Maintain clean, concise, and modular code.
- **Test Driven Development**: Use the synthetic QA data to evaluate the accuracy of the retrieval and ingestion components, and to iteratively improve the system.
- **Communication**: Treat the project as if you were a part of the Duckie team. We believe in open communication and collaboration, so don't hesitate to ask questions or bring up ideas!
