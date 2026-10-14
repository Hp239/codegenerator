from google import genai
from config import GEMINI_API_KEY, MODEL_NAME


class AIModel:

    def __init__(self):

        if not GEMINI_API_KEY:
            raise ValueError(
                "Gemini API Key not found. Please check your .env file."
            )

        self.client = genai.Client(
            api_key=GEMINI_API_KEY
        )

    def generate_code(self, prompt):

        try:

            response = self.client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt
            )

            if response.text:
                return response.text

            return "No response generated."

        except Exception as e:
            raise Exception(f"Gemini Error : {e}")


if __name__ == "__main__":

    ai = AIModel()

    prompt = "Write a Python program to print Hello World."

    print(ai.generate_code(prompt))