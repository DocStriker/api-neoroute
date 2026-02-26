from google import genai
from google.genai import types
import json
from app.core.config import get_param

class AIService:

    def __init__(self):
        self.api_token = get_param("/neoroute/api/aiagent")

    def parse(self, texto):
        prompt = f"""
        Extraia localização e tipo de carga:
        {texto}
        """

        client = genai.Client(api_key=self.api_token)

        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=prompt,
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_budget=0)
            ),
        )

        try:
            return json.loads(response.text)
        except:
            return None