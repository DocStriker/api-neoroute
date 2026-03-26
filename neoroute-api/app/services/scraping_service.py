import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from app.utils.utils import Utils

class ScrapingService:
    def __init__(self):
        self.u = Utils()

    def use_bs(self, url):
        try:
            html = requests.get(url, timeout=30).text  # timeout em segundos
            soup = BeautifulSoup(html, "html.parser")

            texto = " ".join([p.get_text() for p in soup.find_all("p")])

            return texto
        except requests.exceptions.ConnectTimeout:
            print(f"Tempo esgotado para {url[:10]}")
        except requests.exceptions.RequestException as e:
            print(f"Erro ao acessar {url[:10]}: {e}")

    def fetch_gdelt(self):

        """usa a API do Gdelt para coletar urls de notícias globais e retorna um dataframe."""
    
        # Formata datas no padrão exigido pela API GDELT

        url = "https://api.gdeltproject.org/api/v2/doc/doc/"
        params = {
            "query": "truck theft sourcecountry:brazil",
            "mode": "artlist",
            "format": "json",
            "timespan": "3d",
            "maxrecords": 250,
            "sort": "datedesc"
        }

        try:
            resp = self.u.safe_request(url, params)
            print(resp.status_code)

            # Verifica se o servidor respondeu corretamente
            if resp.status_code != 200:
                print(f"HTTP {resp.status_code}: {resp.text[:200]}")
                return pd.DataFrame()

            # Tenta decodificar JSON
            try:
                data = resp.json()
            except Exception:
                print("Erro ao converter resposta em JSON.")
                print("Resposta recebida:")
                print(resp.text[:500])
                return pd.DataFrame()

            # Verifica se há artigos
            if "articles" not in data or not data["articles"]:
                print("Nenhum artigo encontrado na resposta do GDELT.")
                return pd.DataFrame()

            # Converte para DataFrame
            articles = pd.DataFrame(data["articles"]).rename(columns={'seendate':'date'})

            def parse_pubdate(pubdate_str):
                try:
                    return datetime.strptime(pubdate_str, "%Y%m%dT%H%M%SZ").strftime("%Y-%m-%d")
                except Exception:
                    return None

            articles["date"] = articles["date"].map(parse_pubdate)
            articles.dropna(subset=["date"], inplace=True)
            articles.drop_duplicates(inplace=True)

            return articles[["url", "date"]]

        except requests.RequestException as e:
            print(f"Erro de conexão com GDELT: {e}")

            return pd.DataFrame() # Retorno em dataframe