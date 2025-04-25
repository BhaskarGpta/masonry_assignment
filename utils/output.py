import json
import re
from typing import Dict

class OutputHadler: #Remove ```json and ``` using regex or strip'''
    @staticmethod
    def clean_llm_output(raw_output: str) -> dict:
        cleaned = re.sub(r"^```json\s*|\s*```$", "", raw_output.strip(), flags=re.IGNORECASE)
        return json.loads(cleaned)