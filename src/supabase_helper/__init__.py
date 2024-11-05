import os
import warnings

from supabase import Client, create_client


def get_supabase() -> Client:
    warnings.simplefilter("ignore", ResourceWarning)
    return create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

'''
Example usage:

# Get the supabase client
supabase = get_supabase()

# Fetch data from a table
data = supabase.table("my_table").select("*").execute().data
print(data)

# Insert data into a table
supabase.table("my_table").insert({"name": "John", "age": 30}).execute()
'''
