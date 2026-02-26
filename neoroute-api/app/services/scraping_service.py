import requests
import pandas as pd
from datetime import datetime, timedelta

class ScrapingService:

    def fetch_gdelt(self):
        end_time = datetime.now()
        start_time = end_time - timedelta(days=3)

        url = "https://api.gdeltproject.org/api/v2/doc/doc/"
        params = {
            "query": "truck theft sourcecountry:brazil",
            "mode": "ArtList",
            "format": "json",
            "startdatetime": start_time.strftime("%Y%m%d%H%M%S"),
            "enddatetime": end_time.strftime("%Y%m%d%H%M%S"),
        }

        resp = requests.get(url, params=params, timeout=15)
        if resp.status_code != 200:
            return pd.DataFrame()

        data = resp.json()
        if "articles" not in data:
            return pd.DataFrame()

        df = pd.DataFrame(data["articles"])
        df.rename(columns={"seendate": "date"}, inplace=True)
        return df[["url", "date"]]