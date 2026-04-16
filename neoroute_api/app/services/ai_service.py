from pydantic import BaseModel, Field, ValidationError
from dotenv import load_dotenv
import json, os, requests

import logging
logger = logging.getLogger(__name__)

load_dotenv()

class ReviewAnalysis(BaseModel):
            street: str = Field(description="The street where the location is situated, if not found, return 'unknown'")
            city: str = Field(description="The city where the location is situated, if not found, return 'unknown'")
            state: str = Field(description="The state where the location is situated in its abbreviated form, e.g., SP for São Paulo, if not found, return 'unknown'")
            cargo_type: str = Field(description="The type of cargo stolen, in a single word without accents and in plural, if not found, return 'unknown'")

class AIService:
    def __init__(self):
        self.api_token = os.getenv("AIAGENT_TOKEN_TWO")
        self.url = "https://openrouter.ai/api/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        
    def parse(self, texto):  
        prompt = f"""
                Extract structured data from the text below.

                Text:
                {texto}

                Return ONLY a valid JSON with this structure:
                {{
                "street": "string",
                "city": "string",
                "state": "string",
                "cargo_type": "string"
                }}

                Rules:
                - must be use 'unknown' if not found
                - cargo_type must be ONE word, plural, no accents and related to the type of cargo stolen (e.g., electronics, furniture, etc.)
                - state must be abbreviated (e.g., SP)
                """
             
        response = requests.post(self.url, headers=self.headers, timeout=15, json={
                    "model": "nvidia/nemotron-3-super-120b-a12b:free",
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "reasoning": {"enabled": False}
                    }
                )
        logger.info(f"AI response status: {response.status_code}")
        response.raise_for_status()

        content = response.json()["choices"][0]["message"]["content"]

        try:
            data = json.loads(content)
            return ReviewAnalysis(**data)

        except (json.JSONDecodeError, ValidationError):
            return ReviewAnalysis()
        
if __name__ == "__main__":
    ai_service = AIService()
    test_text = "Roubo de carga de eletrônicos na Av. Paulista, São Paulo, SP."
    result = ai_service.parse(test_text)
    print(result.model_dump())