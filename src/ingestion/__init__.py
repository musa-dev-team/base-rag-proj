# from src.duckie_objects.threads.thread_obj import DuckieThread


# class ExampleStringIngestor:
#     def __init__(self, string: str):
#         self.string = string

#     def ingest(self):
#         pass

# class ExampleThreadIngestor:
#     def __init__(self, thread_obj: DuckieThread):
#         self.thread_obj = thread_obj

#     def ingest(self):
#         self.pre_process()
#         self.generate_embeddings()
#         self.insert_data()

#     def pre_process(self):
        
#         pass

#     def generate_embeddings(self):
        
#         pass

#     def insert_data(self):

#         pass


import re
import json
from typing import List, Dict
from sentence_transformers import SentenceTransformer
import chromadb
import chromadb.utils.embedding_functions as embedding_functions

class MarkdownChunker:
    def __init__(self):
        # Regex for detecting headers (#, ##, etc.)
        self.header_pattern = re.compile(r'^(#{1,6})\s+(.+)$')
        # Regex for detecting code blocks (```)
        self.code_block_start_pattern = re.compile(r'^```.*$')
        # Regex for detecting list items (-, *, 1., etc.)
        self.list_item_pattern = re.compile(r'^\s*([-*]|\d+\.)\s+(.+)$')
        # Initialize the SentenceTransformer model for embeddings
        self.embedding_model = SentenceTransformer('all-MiniLM-L12-v2')
        # Initialize Chroma DB client
        self.chroma_client = chromadb.Client()
        # Initialize or get the Duckie collection
        self.collection = self.chroma_client.get_or_create_collection(name="Duckie")

    def chunk_markdown(self, content: str) -> List[Dict[str, str]]:
        """
        Chunks Markdown content into sections based on headers, lists, code blocks, and paragraphs.
        Includes metadata with the section title for each chunk.
        Returns a list of chunks, each with type, content, and metadata.
        """
        lines = content.splitlines()
        chunks = []
        current_chunk = []
        current_type = None
        current_section_title = ""  # Track the current section title
        in_code_block = False
        in_list = False

        for line in lines:
            line = line.rstrip()

            # Handle empty lines (potential paragraph breaks)
            if not line.strip():
                if current_chunk:
                    # Finish the current chunk (if not in a code block or list)
                    if not in_code_block and not in_list:
                        self._add_chunk(chunks, current_type, current_chunk, current_section_title)
                        current_chunk = []
                        current_type = None
                continue

            # Handle code blocks
            if self.code_block_start_pattern.match(line):
                if in_code_block:
                    # End of code block
                    current_chunk.append(line)
                    self._add_chunk(chunks, "code", current_chunk, current_section_title)
                    current_chunk = []
                    current_type = None
                    in_code_block = False
                else:
                    # Start of code block
                    if current_chunk:
                        self._add_chunk(chunks, current_type if current_type else "paragraph", current_chunk, current_section_title)
                    current_chunk = [line]
                    current_type = "code"
                    in_code_block = True
                continue

            if in_code_block:
                current_chunk.append(line)
                continue

            # Handle headers
            header_match = self.header_pattern.match(line)
            if header_match:
                if current_chunk:
                    self._add_chunk(chunks, current_type if current_type else "paragraph", current_chunk, current_section_title)
                # Extract the header text as the new section title
                current_section_title = header_match.group(2).strip()
                current_chunk = [line]
                current_type = "header"
                in_list = False
                continue

            # Handle lists
            list_match = self.list_item_pattern.match(line)
            if list_match:
                if not in_list and current_chunk:
                    self._add_chunk(chunks, current_type if current_type else "paragraph", current_chunk, current_section_title)
                    current_chunk = []
                    current_type = "list"
                current_chunk.append(line)
                in_list = True
                continue
            else:
                if in_list:
                    # End of list
                    self._add_chunk(chunks, "list", current_chunk, current_section_title)
                    current_chunk = [line]
                    current_type = "paragraph"
                    in_list = False
                else:
                    current_chunk.append(line)

        # Handle any remaining content
        if current_chunk:
            self._add_chunk(chunks, current_type if current_type else "paragraph", current_chunk, current_section_title)

        return chunks

    def _add_chunk(self, chunks: List[Dict[str, str]], chunk_type: str, chunk_lines: List[str], section_title: str):
        """
        Helper method to add a chunk to the chunks list with metadata.
        """
        if chunk_lines:
            chunks.append({
                "type": chunk_type,
                "content": "\n".join(chunk_lines).strip(),
                "metadata": {
                    "section_title": section_title
                }
            })

    def process_json_records(self, json_file_path: str) -> List[Dict]:
        """
        Process a JSON file containing records and chunk the 'Content' field of each record.
        Returns a list of records with an additional 'chunks' field, including metadata.
        """
        processed_records = []

        # Read JSON file
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                records = json.load(f)
        except FileNotFoundError:
            print(f"Error: File '{json_file_path}' not found.")
            return []
        except json.JSONDecodeError:
            print(f"Error: File '{json_file_path}' contains invalid JSON.")
            return []

        for record in records:
            # Ensure required fields exist
            if "content" not in record:
                print(f"Skipping record with missing 'content': {record.get('title', 'Unknown')}")
                continue

            # Chunk the Markdown content
            content = record["content"]
            chunks = self.chunk_markdown(content)

            # Add chunks to the record
            processed_record = record.copy()
            processed_record["chunks"] = chunks
            processed_records.append(processed_record)

        return processed_records
    
    def embed_and_upsert_to_chroma(self, processed_records: List[Dict]):
        """
        Converts chunks from processed records to vector embeddings using MiniLM-L12-v2
        and upserts them into Chroma DB (Duckie collection).
        Each chunk's content, metadata, and embedding is stored.
        """
        documents = []
        metadatas = []
        ids = []
        chunk_id = 0

        for record in processed_records:
            # Use lowercase field names as per handbook.json structure
            source_title = record.get("title", "Unknown")
            source_url = record.get("url", "Unknown")
            for chunk in record["chunks"]:
                chunk_content = chunk["content"]
                chunk_type = chunk["type"]
                chunk_section_title = chunk["metadata"]["section_title"]

                # Ensure all metadata values are strings and handle None
                metadata = {
                    "source_title": str(source_title if source_title is not None else ""),
                    "source_url": str(source_url if source_url is not None else ""),
                    "chunk_type": str(chunk_type if chunk_type is not None else ""),
                    "section_title": str(chunk_section_title if chunk_section_title is not None else "")
                }

                # Debug: Check for invalid metadata values
                for key, value in metadata.items():
                    if not isinstance(value, (str, int, float, bool)):
                        print(f"Warning: Invalid metadata value for {key}: {value} (type: {type(value)}) in chunk {chunk_id}")

                # Append to lists for upsert
                documents.append(chunk_content)
                metadatas.append(metadata)
                ids.append(f"chunk_{chunk_id}")
                chunk_id += 1

        # Generate embeddings for all chunks
        embeddings = self.embedding_model.encode(documents, show_progress_bar=True)

        # Upsert to Chroma DB
        try:
            self.collection.upsert(
                ids=ids,
                documents=documents,
                embeddings=embeddings.tolist(),
                metadatas=metadatas
            )
            print(f"Successfully upserted {len(ids)} chunks into Chroma DB (Duckie collection).")
        except Exception as e:
            print(f"Error upserting chunks to Chroma DB: {str(e)}")

    def retrieve_relevant_chunks(self, query: str, n_results: int = 3) -> List[Dict]:
        """
        Retrieves the top N most relevant chunks for a given query from Chroma DB.
        Returns a list of dictionaries containing the chunk content, metadata, and distance.
        """
        # Embed the query
        query_embedding = self.embedding_model.encode([query])[0]

        # Query Chroma DB
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=n_results
        )

        # Format the results
        retrieved_chunks = []
        for i in range(len(results["documents"][0])):
            chunk_info = {
                "content": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i]
            }
            retrieved_chunks.append(chunk_info)

        return retrieved_chunks

def main():
    """
    Main function to test the MarkdownChunker class.
    Creates a sample JSON file, processes it, and prints the chunked results.
    """
    # Create an instance of MarkdownChunker
    chunker = MarkdownChunker()

    # Write example data to a file
    json_file_path = "data/raw/docs/handbook.json"

    # Process the JSON file using MarkdownChunker
    processed_records = chunker.process_json_records(json_file_path)

    # Print the results
    if not processed_records:
        print("No records processed.")
        return

    # for record in processed_records:
    #     print(f"\nTitle: {record['title']}")
    #     print(f"URL: {record['url']}")
    #     print("Chunks:")
    #     for chunk in record["chunks"]:
    #         print(f"  Type: {chunk['type']}")
    #         print(f"  Content: {chunk['content']}")
    #         print(f"  Section Title: {chunk['metadata']['section_title']}")
    #         print("-" * 40)

    # Embed chunks and upsert to Chroma DB
    chunker.embed_and_upsert_to_chroma(processed_records)

    # Path to the JSON file containing questions
    questions_json_path = "data/synthetic_qa/docs/handbook_qa.json"  # Replace with your actual path

    # Read the questions JSON file
    try:
        with open(questions_json_path, 'r', encoding='utf-8') as f:
            questions = json.load(f)
    except FileNotFoundError:
        print(f"Error: Questions file '{questions_json_path}' not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: Questions file '{questions_json_path}' contains invalid JSON.")
        return

    # Process each question and retrieve relevant chunks
    for idx, q in enumerate(questions):
        query = q.get("question", "")
        if not query:
            print(f"Skipping question {idx + 1}: No question provided.")
            continue

        print(f"\nProcessing question {idx + 1}: '{query}'")
        relevant_chunks = chunker.retrieve_relevant_chunks(query, n_results=3)

        # Print the top chunks
        print(f"Top 3 relevant chunks for question '{query}':")
        if not relevant_chunks:
            print("  No relevant chunks found.")
        else:
            for i, chunk in enumerate(relevant_chunks):
                print(f"\nResult {i + 1}:")
                print(f"  Content: {chunk['content']}")
                print(f"  Source Title: {chunk['metadata']['source_title']}")
                print(f"  Source URL: {chunk['metadata']['source_url']}")
                print(f"  Chunk Type: {chunk['metadata']['chunk_type']}")
                print(f"  Section Title: {chunk['metadata']['section_title']}")
                print(f"  Distance: {chunk['distance']}")
                print("-" * 40)

if __name__ == "__main__":
    main()