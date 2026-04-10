import os
from urllib import response
from google import genai
from pydantic import BaseModel, Field, ValidationError
from dotenv import load_dotenv
import json
import requests

load_dotenv()

class ReviewAnalysis(BaseModel):
            street: str = Field(description="The street where the location is situated, if not found, return 'unknown'")
            city: str = Field(description="The city where the location is situated, if not found, return 'unknown'")
            state: str = Field(description="The state where the location is situated in its abbreviated form, e.g., SP for São Paulo, if not found, return 'unknown'")
            cargo_type: str = Field(description="The type of cargo stolen, in a single word without accents and in plural, if not found, return 'unknown'")

class AIService:

    def __init__(self):
        if os.getenv("ENV") == "aws":
            from app.core.ssm_config import get_param
            self.api_token = get_param("/neoroute/api/aiagent")

        self.api_token = os.getenv("AIAGENT_TOKEN_TWO")
        #self.client = genai.Client(api_key=self.api_token)
        self.url = "https://openrouter.ai/api/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }

        
    def parse(self, texto, model="gemini"):
        if model == "gemini":
            prompt = f"No texto: {texto}, extraia a localização principal mencionada no texto, o tipo de carga roubada, a rua, cidade e o estado onde ocorreu o roubo."

            config = genai.types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=ReviewAnalysis,
            thinking_config=genai.types.ThinkingConfig(include_thoughts=False))
                
            response = self.client.models.generate_content(
                model="gemini-3.1-flash-lite-preview",
                contents=prompt,
                config=config)
            return response.parsed
        
        elif model == "openrouter":
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
                - Use 'unknown' if not found
                - cargo_type must be ONE word, plural, no accents
                - state must be abbreviated (e.g., SP)
                """
             
            response = requests.post(self.url, headers=self.headers, timeout=15, json={
                    "model": "nvidia/nemotron-3-nano-30b-a3b:free",
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "reasoning": {"enabled": False}
                    }
                )
            
            response.raise_for_status()

            content = response.json()["choices"][0]["message"]["content"]

            # -------------------------
            # Parsing seguro
            # -------------------------

            try:
                data = json.loads(content)
                return ReviewAnalysis(**data)

            except (json.JSONDecodeError, ValidationError):
                # fallback robusto
                return ReviewAnalysis()
        
if __name__ == "__main__":
    ai_service = AIService()
    test_text = "Roubo de carga de eletrônicos na Av. Paulista, São Paulo, SP."
    result = ai_service.parse(test_text, model="openrouter")
    print(result)