from src.duckie_objects.threads.thread_obj import DuckieThread


class ExampleStringIngestor:
    def __init__(self, string: str):
        self.string = string

    def ingest(self):
        pass

class ExampleThreadIngestor:
    def __init__(self, thread_obj: DuckieThread):
        self.thread_obj = thread_obj

    def ingest(self):
        self.pre_process()
        self.generate_embeddings()
        self.insert_data()

    def pre_process(self):
        pass

    def generate_embeddings(self):
        pass

    def insert_data(self):
        pass