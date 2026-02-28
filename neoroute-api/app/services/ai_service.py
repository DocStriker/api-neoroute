from google import genai
from google.genai import types
import json
from app.core.config import get_param

class AIService:

    def __init__(self):
        self.api_token = get_param("/neoroute/api/aiagent")

    def parse(self, texto):
        prompt = f"""
        No texto: {texto},

        Extraia a localização principal mencionada no texto e retorne
        no seguinte formato: 
        
        ['street': 'Rodovia/Rua', 
        'city': 'cidade' ou ''(caso não tenha), 
        'state': estado (ex: MG), 
        'cargo_type': tipo de carga roubada em só uma palavra sem acentos e no plural (ex: Eletrônicos, Móveis...)] """

        client = genai.Client(api_key=self.api_token)

        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=prompt,
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_budget=0)
            ),
        )

        if response.text:
            try:
                data = json.loads(response.text[8:-3])
            except json.JSONDecodeError as e:
                print("Erro ao decodificar JSON:", e)
                data = None

        return data # Retorno em json