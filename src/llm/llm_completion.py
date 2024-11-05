from abc import abstractmethod


class LLMCompletion:
    def __init__(self):
        pass

    @abstractmethod
    def generate_text(self, **kwargs) -> str: ...

    @abstractmethod
    def get_vision_messages(self, image_data_base64: list) -> list[dict]: ...
