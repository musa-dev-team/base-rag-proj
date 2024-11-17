from dotenv import load_dotenv
from src.weaviate_db import WeaviateDB

load_dotenv(override=True)


weaviate_db = WeaviateDB("test_collection")
all_records = weaviate_db.fetch(limit=100)

# for record in all_records[-1:]:
#     print(record)

total_count = weaviate_db.count()
print(f"Total number of records: {total_count}")

