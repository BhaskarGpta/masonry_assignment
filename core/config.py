from dataclasses import dataclass

class GeminiAPIConfig:
    model: str = "gemini-2.5-flash-preview-04-17"
    max_output_tokens = None
    temperature: float = 0
    timeout= None
    max_retries: int = 10
    retry_delay: int = 10
   
 

