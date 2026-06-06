from openai import OpenAI
import base64
from abc import ABC, abstractmethod

## LlmClient = blueprint / inherited from ABC as a blueprint
class LlmClient(ABC):
    def __init__(self):
        self.client = None

    def encode_image(self, image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    @abstractmethod
    def call_model(self, image_path):
        pass


## Gpt = implementation
class Gpt(LlmClient):

    # Only the initial setup
    def __init__(self, model):
        self.client = OpenAI()
        self.model = model

    # Actual work/implementation
    def call_model(self, image_path):
        base64_str = self.encode_image(image_path)

        try:
            response = self.client.responses.create(
                model = self.model,
                instructions="You will be an image analyzer that analyzes the image that the user uploaded.",
                input=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "input_text", "text": "What is this image about?"},
                            {
                                "type": "input_image",
                                "image_url": f"data:image/jpeg;base64,{base64_str}"
                            }
                        ]
                    }
                ]
            )
        except Exception as e:
            raise RuntimeError(f"Failed to analyze the image with OpenAI - {e}")

        return response.output_text


