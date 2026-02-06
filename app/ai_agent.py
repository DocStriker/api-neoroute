#####################################################################################################
# 1. Importação das bibliotecas principais

import requests
from google import genai
from google.genai import types
from bs4 import BeautifulSoup
import os
import json
from dotenv import load_dotenv

#####################################################################################################
# 2. Configurando variáveis de ambiente

load_dotenv()

api_token = os.getenv('GENAI_TOKEN')

#####################################################################################################
# 3. Funções de utilidades

# Função para testa um scrap em uma url e retira o texto dela
def TestingScrap():
    """retorna o texto da url como string."""

    url = 'https://g1.globo.com/mt/mato-grosso/noticia/2025/09/24/roubos-de-carga-de-caminhao-tem-queda-de-mais-de-40percent-com-ajuda-de-tecnologia-em-mt.ghtml'

    html = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}).text
    soup = BeautifulSoup(html, "html.parser")

    texto = " ".join([p.get_text() for p in soup.find_all("p")])

    return texto

# Agente Gemini da Google
def ParseToAgent(texto, api_token):
    """recebe o 'texto' como parte do prompt e retorna um json da resposta. 'api_token' -> token da API"""
    
    prompt = f"""
        No texto: {texto},

        Extraia a localização principal mencionada no texto e retorne
        no seguinte formato: 
        
        ['street': 'Rodovia/Rua', 'city': 'cidade' ou ''(caso não tenha), 'state': estado (ex: MG), 'cargo_type': tipo de carga roubada em só uma palavra sem acentos e no plural (ex: Eletrônicos, Móveis...)] """
        

    client = genai.Client(api_key=api_token)
    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=prompt,
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=0)  # Desabilita o modo pensamento
        ),
    )

    if response.text:
        try:
            data = json.loads(response.text[8:-3])
        except json.JSONDecodeError as e:
            print("Erro ao decodificar JSON:", e)
            data = None

    return data # Retorno em json

#####################################################################################################

if __name__ == '__main__':
    texto = TestingScrap()
    print(ParseToAgent(texto, api_token=api_token))