import json

from app.services.scraping_service import ScrapingService
from app.services.ai_service import AIService
from app.services.geolocation_service import GeolocationService
from app.utils.utils import Utils, RateLimiter
from app.repositories.database import get_connection, release_connection
from app.models.db_models import init_db

class AgentService:

    def __init__(self):
        self.scraper = ScrapingService()
        self.ai = AIService()
        self.geo = GeolocationService()
        self.u = Utils()
        self.rate_limiter = RateLimiter(max_calls=10, period=60)  # Limite de 10 chamadas por minuto

    def run(self):

        try:
            df = self.scraper.fetch_gdelt()

            init_db()
            print(f"{'DB Initiated. Starting Agent...'}")

            conn = get_connection()
            cur = conn.cursor()

            for _, row in df.iterrows():

                print("Processando:", row["url"][7:30], "...")

                cur.execute("SELECT 1 FROM rotas WHERE url = %s", (row["url"],))
                rota_existente = cur.fetchone()

                if rota_existente:
                    print(f"Url já existe no banco: {row['url'][:10]} ...")
                    continue
                
                texto = self.scraper.use_bs(row["url"])

                self.rate_limiter.wait()  # Aguarda se necessário para respeitar o limite de chamadas

                airesponse = self.ai.parse(texto) if texto else None

                print(f"Agent Response: {airesponse}")

                state = airesponse.state

                coord = self.geo.get_coordinates(self.u.extract_adress(airesponse))
                coord = json.dumps(coord) if isinstance(coord, dict) else str(coord)

                cargo_list = [c.strip() for c in airesponse.cargo_type.split(",") if c.strip()]

                # Insere rota
                cur.execute(
                    "INSERT INTO rotas (url, state, date, coord) VALUES (%s, %s, %s, %s) RETURNING id;",
                    (row["url"], state, row["date"], coord)
                )
                rota_id = cur.fetchone()[0]

                # Insere cada carga e vincula à rota
                # Para cada carga
                for cargo in cargo_list:
                    cargo = self.u.remove_acentos(cargo.strip().lower())  # normaliza (evita duplicados tipo "Combustível" vs "combustivel")

                        # Insere ou ignora se já existir
                    cur.execute("""
                        INSERT INTO cargas (nome)
                        VALUES (%s)
                        ON CONFLICT (nome) DO NOTHING;
                    """, (cargo,))

                    # Busca o id (mesmo se já existia)
                    cur.execute("SELECT id FROM cargas WHERE nome = %s;", (cargo,))
                    cargo_id = cur.fetchone()[0]

                    # Associa à rota
                    cur.execute("""
                        INSERT INTO rota_cargas (rota_id, carga_id)
                        VALUES (%s, %s)
                        ON CONFLICT DO NOTHING;
                    """, (rota_id, cargo_id))
                    
                    print(f"Rota registrada.")
                # Salva no banco RDS
                conn.commit()
                
            print('Concluído.')

            # Fecha as conexões
            cur.close()
            release_connection(conn)

        except Exception as e:
            print("Agent Service Error:", str(e))
            raise e