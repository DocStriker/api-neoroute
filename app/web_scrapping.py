#####################################################################################################
# 1. Importação das bibliotecas

import requests
import pandas as pd
from datetime import datetime, timedelta

#####################################################################################################
# 2. Funções das APIs

# Função da API do Gdelt para coleta de notícias
def searchFromGdelt():
    """usa a API do Gdelt para coletar urls de notícias globais e retorna um dataframe."""
    end_time = datetime.now()
    start_time = end_time - timedelta(days=3)

    # Formata datas no padrão exigido pela API GDELT
    start_str = start_time.strftime("%Y%m%d%H%M%S")
    end_str = end_time.strftime("%Y%m%d%H%M%S")

    url = "https://api.gdeltproject.org/api/v2/doc/doc/"
    params = {
        "query": "truck theft sourcecountry:brazil",
        "mode": "ArtList",
        "format": "json",
        "startdatetime": start_str,
        "enddatetime": end_str
    }

    print(f"Buscando artigos de {start_time} até {end_time}...")

    try:
        resp = requests.get(url, params=params, timeout=15)

        # 🔍 Verifica se o servidor respondeu corretamente
        if resp.status_code != 200:
            print(f"HTTP {resp.status_code}: {resp.text[:200]}")
            return pd.DataFrame()

        # 🔍 Tenta decodificar JSON
        try:
            data = resp.json()
        except Exception:
            print("Erro ao converter resposta em JSON.")
            print("Resposta recebida:")
            print(resp.text[:500])
            return pd.DataFrame()

        # 🔍 Verifica se há artigos
        if "articles" not in data or not data["articles"]:
            print("⚠️ Nenhum artigo encontrado na resposta do GDELT.")
            return pd.DataFrame()

        # Converte para DataFrame
        articles = pd.DataFrame(data["articles"])

        def parse_pubdate(pubdate_str):
            try:
                return datetime.strptime(pubdate_str, "%Y%m%dT%H%M%SZ").strftime("%Y-%m-%d")
            except Exception:
                return None

        articles["seendate"] = articles["seendate"].map(parse_pubdate)
        articles.dropna(subset=["seendate"], inplace=True)
        articles.drop_duplicates(inplace=True)

        return articles[["url", "seendate"]]

    except requests.RequestException as e:
        print(f"Erro de conexão com GDELT: {e}")

        return pd.DataFrame() # Retorno em dataframe

# Função para agrupar e normalizar as informações gerais do dataframe
def Scrap():
    gdelt_df = searchFromGdelt().rename(columns={'seendate':'date'})

    return gdelt_df # Retorno em dataframe

#####################################################################################################

if __name__ == "__main__":
    df = Scrap()
    print(df.head(), "\n", "-" * 65)
    df.info()