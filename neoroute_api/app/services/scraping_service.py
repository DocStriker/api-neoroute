import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from app.utils.utils import Utils

import logging
logger = logging.getLogger(__name__)

class ScrapingService:
    def __init__(self):
        self.u = Utils()

    def use_bs(self, url):
        try:
            html = requests.get(url, timeout=20).text
            soup = BeautifulSoup(html, "html.parser")

            texto = " ".join([p.get_text() for p in soup.find_all("p")])

            return texto
        except requests.exceptions.ConnectTimeout:
            print(f"Tempo esgotado para {url[:10]}")
        except requests.exceptions.RequestException as e:
            print(f"Erro ao acessar {url[:10]}: {e}")

    def fetch_gdelt(self):
        url = "https://api.gdeltproject.org/api/v2/doc/doc/"
        params = {
            "query": "truck theft sourcecountry:brazil",
            "mode": "artlist",
            "format": "json",
            "timespan": "7d",
            "maxrecords": 250,
        }

        try:
            resp = self.u.safe_request(url, params)
            data = resp.json()

            if "articles" not in data or not data["articles"]:
                logger.info("No articles found in GDELT response")

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
            logger.error("Connection error with GDELT: %s", e)
            return None
        
        except Exception as e:
            logger.error("Unexpected error: %s", e)
            return None
