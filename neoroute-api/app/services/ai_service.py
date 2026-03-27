from http import client
import os
from google import genai
from google.genai import types
import json
from pydantic import BaseModel, Field
from app.core.config import get_param
from dotenv import load_dotenv
load_dotenv()

class AIService:

    def __init__(self):
        if os.getenv("ENV") == "aws":
            self.api_token = get_param("/neoroute/api/aiagent")
        self.api_token = os.getenv("AIAGENT_TOKEN")
        
    def parse(self, texto):
        prompt = f"""
        No texto: {texto}, extraia a localização principal mencionada no texto, o tipo de carga roubada, a rua, cidade e o estado onde ocorreu o roubo."""

        client = genai.Client(api_key=self.api_token)

        class ReviewAnalysis(BaseModel):
            street: str = Field(description="The street where the location is situated")
            city: str = Field(description="The city where the location is situated")
            state: str = Field(description="The state where the location is situated")
            cargo_type: str = Field(description="The type of cargo stolen, in a single word without accents and in plural")
            

        response = client.models.generate_content(
            model="gemini-3.1-flash-lite-preview",
            contents=prompt,
            config={"response_mime_type": "application/json",
        "response_json_schema": ReviewAnalysis.model_json_schema()}
        )

        return response.text
'''
        if result:
            try:
                data = json.loads(result)
                return data # Retorno em json
            except json.JSONDecodeError as e:
                print("Erro ao decodificar JSON:", e)
                data = None
                return data
'''
        