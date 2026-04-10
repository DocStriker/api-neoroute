import json, re, datetime

from app.services.scraping_service import ScrapingService
from app.services.geolocation_service import GeolocationService
from app.utils.utils import Utils, RateLimiter
from app.utils.filters import Filters
from app.repositories.database import get_connection, release_connection

import logging
logger = logging.getLogger(__name__)

class AgentService:

    def __init__(self):
        self.scraper = ScrapingService()
        self.geo = GeolocationService()
        self.u = Utils()
        self.f = Filters()
        self.rate_limiter = RateLimiter(max_calls=10, period=60)

    def run(self):
        try:
            logger.info("Fetching GDELT data and initializing...")
            df = self.scraper.fetch_gdelt()

            if df is None or df.empty:
                raise Exception("No data fetched from GDELT.")

            conn = get_connection()
            cur = conn.cursor()

            logger.info("DB initiated. Agent started at %s", datetime.datetime.now())
            logger.info("Total URLs to process: %d", len(df))

            for _, row in df.iterrows():
                try:
                    if not self.f.is_relevant_url(row["url"]):
                        logger.info("Irrelevant URL, skipping: %s", row['url'], extra={"url": row["url"]})
                        continue

                    logger.info("Processing: %s", row['url'], extra={"url": row["url"]})
                    text = self.scraper.use_bs(row["url"])

                    if not self.f.is_valid_text(text):
                        logger.info("Invalid text or too short, skipping url: %s", row['url'], extra={"url": row["url"]})
                        continue

                    h = self.u.hash(row["url"])

                    cur.execute("SELECT processed, response FROM process_cache WHERE hash = %s", (h,))
                    cached = cur.fetchone()

                    logger.info("Cache %s for hash: %s", "hit" if cached else "miss", h)

                    if cached and cached[0]:
                        logger.info("FULL CACHE HIT → skipping processing \n")
                        continue
                    
                    else:
                        airesponse = self.rate_limiter.safe_ai_call(text).model_dump()
                        logger.info("AI response obtained for hash: %s, response: %s", h, airesponse)

                        cur.execute(
                            "INSERT INTO process_cache (hash, response, processed) VALUES (%s, %s, %s)",
                            (h, json.dumps(airesponse), True)
                        )

                    state = airesponse.get("state")
                    cargo = airesponse.get("cargo_type")

                    if state == "unknown" or cargo == "unknown":
                        logger.info("State or Cargo Type not found in AI response, skipping URL: %s", row['url'], extra={"url": row["url"]})
                        continue

                    coord = self.geo.get_coordinates(self.f.extract_adress(airesponse))
                    coord = json.dumps(coord) if isinstance(coord, dict) else str(coord)

                    cargo_list = re.split(r"[,\s]+", cargo)
                    cargo_list = [c.strip() for c in cargo_list if c.strip()]

                    logger.info("Extracted state: %s, cargo types: %s, coordinates: %s", state, cargo_list, coord)

                    cur.execute(
                                """
                                INSERT INTO rotas (url, state, date, coord)
                                VALUES (%s, %s, %s, %s)
                                RETURNING id;
                                """,
                                (row["url"], state, row["date"], coord if coord != "None" else json.dumps({"error": "not found"}))
                            )
                    rota_id = cur.fetchone()[0]
                    logger.info("Route ID %s inserted for URL: %s...", rota_id, row['url'], extra={"url": row["url"]})

                    for cargo in cargo_list:
                        cargo = self.f.remove_accents(cargo.strip().lower())

                        cur.execute("""
                            INSERT INTO cargas (nome)
                            VALUES (%s)
                            ON CONFLICT (nome) DO UPDATE SET nome = EXCLUDED.nome
                            RETURNING id;
                        """, (cargo,))

                        cargo_id = cur.fetchone()[0]

                        cur.execute("""
                            INSERT INTO rota_cargas (rota_id, carga_id)
                            VALUES (%s, %s)
                            ON CONFLICT DO NOTHING;
                        """, (rota_id, cargo_id))
                    
                    conn.commit()
                    logger.info("Registered route. \n")

                        
                except Exception as e:
                    logger.error("Error processing URL %s: %s", row['url'], str(e), extra={"url": row["url"]})
                    conn.rollback()

            conn.commit()
            logger.info("Completed. \n")

        except Exception as e:
            logger.error("Agent Service Error: %s", str(e))
            return {"error": str(e)}

        finally:
            if cur:
                cur.close()
            if conn:
                release_connection(conn)
            return {"message": "agent run completed"}

        