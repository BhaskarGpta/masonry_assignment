import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from .config import GeminiAPIConfig  #LOad config file

class LLMInitializer:
    """
    Initializes the ChatGoogleGenerativeAI language model.
    """
    def __init__(self):
        load_dotenv()  # Load environment variables from .env file
        self.config = GeminiAPIConfig()

        try:
            self.api_key = os.getenv("GOOGLE_API_KEY")
            if not self.api_key:
                raise ValueError("GOOGLE_API_KEY not found in environment variables.")
        except Exception as e:
            raise ValueError(f"Error loading GOOGLE_API_KEY: {e}")

    def set_llm(self) -> ChatGoogleGenerativeAI:
        llm = ChatGoogleGenerativeAI(
            model=self.config.model,  # Corrected to use model_name
            temperature=self.config.temperature,
            max_output_tokens=self.config.max_output_tokens,
            timeout=self.config.timeout,  # Corrected to use timeout
            max_retries=self.config.max_retries,
            google_api_key=self.api_key
        )
        return llm