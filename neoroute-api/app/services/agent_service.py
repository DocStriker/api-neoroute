from app.services.scraping_service import ScrapingService
from app.services.ai_service import AIService
from app.services.geolocation_service import GeolocationService
from app.utils.utils import Utils
from app.repositories.database import get_connection

class AgentService:

    def __init__(self):
        self.scraper = ScrapingService()
        self.ai = AIService()
        self.geo = GeolocationService()

    def run(self):
        df = self.scraper.fetch_gdelt()

        for _, row in df.iterrows():
            # aqui entraria persistência via repository
            print("Processando:", row["url"])