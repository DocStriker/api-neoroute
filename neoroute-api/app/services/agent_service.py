import json, re, datetime

from app.services.scraping_service import ScrapingService
from app.services.geolocation_service import GeolocationService
from app.utils.utils import Utils, RateLimiter
from app.utils.filters import Filters
from app.repositories.database import get_connection, release_connection
from app.models.db_models import init_db

class AgentService:

    def __init__(self):
        self.scraper = ScrapingService()
        self.geo = GeolocationService()
        self.u = Utils()
        self.f = Filters()
        self.rate_limiter = RateLimiter(max_calls=10, period=60)  # Limite de 10 chamadas por minuto

    def run(self):
        try:
            print("Fetching GDELT data and initializing...")
            df = self.scraper.fetch_gdelt()

            init_db()

            conn = get_connection()
            cur = conn.cursor()

            print(f"DB initiated. Agent started at {datetime.datetime.now()}...")
            print(f"{'Total URLs to process:':<25} {len(df)}")

            for _, row in df.iterrows():
                

                try:
                    if not self.f.is_relevant_url(row["url"]):
                        print(f"Url irrelevante, pulando: {row['url'][:30]} ...")
                        continue

                    print("Processando:", row["url"][:30], "...")
                    
                    texto = self.scraper.use_bs(row["url"])

                    if not self.f.is_valid_text(texto):
                        print(f"Texto inválido ou muito curto, pulando url: {row['url'][:30]} ...")
                        continue

                    h = self.u.hash_text(texto)

                    cur.execute("SELECT response FROM ai_cache WHERE hash = %s", (h,))
                    cached = cur.fetchone()
                    print(f"Cache {'hit' if cached else 'miss'} for hash: {h}")

                    if cached:
                        airesponse = json.loads(cached[0])
                        print(f"Using cached response for hash: {h}")
                    else:
                        airesponse = self.rate_limiter.safe_ai_call(texto)
                        print(f"AI response obtained for hash: {h}, response: {airesponse}")

                        cur.execute(
                            "INSERT INTO ai_cache (hash, response) VALUES (%s, %s)",
                            (h, airesponse)
                        )

                    try:
                        if not airesponse or not airesponse.state:
                            continue
                    except Exception:
                        continue

                    print(f"Agent Response: {airesponse}")

                    state = airesponse.state

                    coord = self.geo.get_coordinates(self.f.extract_adress(airesponse))
                    coord = json.dumps(coord) if isinstance(coord, dict) else str(coord)

                    cargo_list = re.split(r"[,\s]+", airesponse.cargo_type)
                    cargo_list = [c.strip() for c in cargo_list if c.strip()]

                    # Insere rota
                    cur.execute(
                        "INSERT INTO rotas (url, state, date, coord) VALUES (%s, %s, %s, %s) RETURNING id ON CONFLICT (url) DO NOTHING;",
                        (row["url"], state, row["date"], coord)
                    )
                    rota_id = cur.fetchone()[0]

                    # Insere cada carga e vincula à rota
                    for cargo in cargo_list:
                        cargo = self.f.remove_acentos(cargo.strip().lower())  # normaliza (evita duplicados tipo "Combustível" vs "combustivel")

                        # Insere ou ignora o nome da carga se já existir
                        cur.execute("""
                            INSERT INTO cargas (nome)
                            VALUES (%s)
                            ON CONFLICT (nome) DO UPDATE SET nome = EXCLUDED.nome
                            RETURNING id;
                        """, (cargo,))

                        cargo_id = cur.fetchone()[0]

                        # Associa à rota
                        cur.execute("""
                            INSERT INTO rota_cargas (rota_id, carga_id)
                            VALUES (%s, %s)
                            ON CONFLICT DO NOTHING;
                        """, (rota_id, cargo_id))
                    
                    # Salva no banco
                    conn.commit()
                    print(f"Rota registrada.")

                        
                except Exception as e:
                    print(f"Error processing URL {row['url'][:30]}: {str(e)}")
                    conn.rollback()  # Reverte apenas a transação atual, mantendo o progresso anterior

            conn.commit()  # Garante que as últimas inserções sejam salvas
            print('Concluído.')

        except Exception as e:
            print("Agent Service Error:", str(e))
            raise e

        finally:
            if cur:
                cur.close()
            if conn:
                release_connection(conn)

        