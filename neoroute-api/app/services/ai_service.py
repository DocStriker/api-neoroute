import os
from google import genai
from pydantic import BaseModel, Field
from app.core.config import get_param
from dotenv import load_dotenv

load_dotenv()

class ReviewAnalysis(BaseModel):
            street: str = Field(description="The street where the location is situated, if not found, return 'unknown'")
            city: str = Field(description="The city where the location is situated, if not found, return 'unknown'")
            state: str = Field(description="The state where the location is situated in its abbreviated form, e.g., SP for São Paulo, if not found, return 'unknown'")
            cargo_type: str = Field(description="The type of cargo stolen, in a single word without accents and in plural, if not found, return 'unknown'")

class AIService:

    def __init__(self):
        if os.getenv("ENV") == "aws":
            self.api_token = get_param("/neoroute/api/aiagent")
        self.api_token = os.getenv("AIAGENT_TOKEN")
        self.client = genai.Client(api_key=self.api_token)
        
    def parse(self, texto):
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
        