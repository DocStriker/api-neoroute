import json, re, datetime

from app.services.scraping_service import ScrapingService
from app.services.geolocation_service import GeolocationService
from app.utils.utils import Utils, RateLimiter
from app.utils.filters import Filters
from sqlalchemy.orm import Session
from app.repositories.process_cache_repository import ProcessCacheRepository
from app.repositories.rota_repository import RotaRepository
from app.repositories.carga_repository import CargaRepository
from app.services.job_service import JobService


import logging
logger = logging.getLogger(__name__)

class AgentService:

    def __init__(self):
        self.scraper = ScrapingService()
        self.geo = GeolocationService()
        self.u = Utils()
        self.f = Filters()
        self.rate_limiter = RateLimiter(max_calls=10, period=60)

    def run(self, job_id: str, db: Session):
        try:
            JobService.update_job(job_id, "running")
            
            logger.info("Running agent, start at %s", datetime.datetime.now())
            logger.info("Fetching GDELT data")

            df = self.scraper.fetch_gdelt()

            if df is None or df.empty:
                raise Exception("No data fetched")

            for _, row in df.iterrows():
                self._process_row(row, db)

            logger.info("Agent finished processing, end at %s", datetime.datetime.now())
            JobService.update_job(job_id, "done")

        except Exception as e:
            logger.error(f"Agent error: {e}")
            JobService.update_job(job_id, "error")

    def _process_row(self, row, db: Session):
        try:
            url = row["url"]

            logger.info("Processing URL: %s", url[:30], extra={"url": " | " + url})

            if not self.f.is_relevant_url(url):
                logger.info("URL not relevant, skipping")
                return

            text = self.scraper.use_bs(url)

            if not self.f.is_valid_text(text):
                logger.info("Text not valid, skipping")
                return

            h = self.u.hash(url)

            cached = ProcessCacheRepository.get(h, db)

            if cached and cached.processed:
                logger.info("URL already processed, skipping")
                return

            airesponse = self.rate_limiter.safe_ai_call(text).model_dump()

            ProcessCacheRepository.save(h, airesponse, db)

            logger.info("Hash for URL: %s", h)
            logger.info("AI response: %s", airesponse)

            state = airesponse.get("state")
            cargo = airesponse.get("cargo_type")

            if state == "unknown" or cargo == "unknown":
                return

            coord = self._resolve_coord(airesponse)

            rota = RotaRepository.create(
                db,
                url=url,
                state=state,
                date=row["date"],
                coord=coord
            )

            self._process_cargos(db, rota.id, cargo)

            db.commit()

        except Exception as e:
            logger.error(f"Error processing row: {e}")
            db.rollback()

    def _resolve_coord(self, airesponse):
        coord = self.geo.get_coordinates(
            self.f.extract_adress(airesponse)
        )

        if isinstance(coord, dict):
            return coord

        return {"error": "not found"}
    
    def _process_cargos(self, db: Session, rota_id: int, cargo_str: str):
        cargos = re.split(r"[,\s]+", cargo_str)

        for cargo in cargos:
            cargo = self.f.remove_accents(cargo.strip().lower())

            carga_obj = CargaRepository.get_or_create(db, cargo)

            RotaRepository.link_carga(db, rota_id, carga_obj.id)

        