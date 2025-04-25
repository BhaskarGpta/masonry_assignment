import os
import json
from typing import Dict

class FileHandler:
    @staticmethod
    def setup_output_directory(input_pdf: str, output_dir: str) -> tuple[str, str]:
        """Create output directory structure and return paths."""
        file_name = os.path.basename(input_pdf).split('.')[0]
        output_subdir = os.path.join(output_dir, file_name)
        os.makedirs(output_subdir, exist_ok=True)
        return file_name, output_subdir

    @staticmethod
    def save_json(data: Dict, filepath: str) -> None:
        """Save dictionary data to JSON file."""
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, "w") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            raise Exception(f"Failed to save JSON file: {str(e)}")

    @staticmethod
    def save_text(content: str, filepath: str) -> None:
        """Save text content to file."""
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, "w") as f:
                f.write(content)
        except Exception as e:
            raise Exception(f"Failed to save text file: {str(e)}")

    @staticmethod
    def load_json(filepath: str) -> Dict:
        """Load JSON data from file."""
        try:
            with open(filepath, "r") as f:
                data = json.load(f)
            return data
        except Exception as e:
            raise Exception(f"Failed to load JSON file: {str(e)}")
    
    @staticmethod
    def load_text(filepath: str) -> str:
        """Load text content from file."""
        try:
            with open(filepath, "r") as f:
                content = f.read()
            return content
        except Exception as e:
            raise Exception(f"Failed to load text file: {str(e)}")