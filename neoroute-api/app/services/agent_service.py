import time, json

from app.services.scraping_service import ScrapingService
from app.services.ai_service import AIService
from app.services.geolocation_service import GeolocationService
from app.utils.utils import Utils
from app.repositories.database import get_connection, release_connection
from app.models.db_models import init_db

class AgentService:

    def __init__(self):
        self.scraper = ScrapingService()
        self.ai = AIService()
        self.geo = GeolocationService()
        self.u = Utils()

    def run(self):

        try:
            df = self.scraper.fetch_gdelt()

            init_db()
            print(f"{'DB Initiated. Starting Agent...'}")

            conn = get_connection()
            cur = conn.cursor()

            contador = 0

            for _, row in df.iterrows():

                print("Processando:", row["url"][7:30], "...")

                cur.execute("SELECT 1 FROM rotas WHERE url = %s", (row["url"],))
                rota_existente = cur.fetchone()

                if rota_existente:
                    print(f"Url já existe no banco: {row['url'][:10]}")
                    continue

                contador += 1

                if contador % 10 == 0:

                    print("\n Atingido 10 requisições. Aguardando 60 segundos...")
                    time.sleep(60)  # pausa de 1 minuto
                    print("Retomando execução...\n")

                texto = self.scraper.use_bs(row["url"])

                airesponse = self.ai.parse(texto) if texto else None

                if isinstance(airesponse, list) and len(airesponse) > 0:
                    airesponse = airesponse[0]

                else:
                    continue

                rjson = self.u.normalize_agent_response(airesponse)

                print(f"Agent Response: {rjson}")

                state = rjson.get("state", "")
                coord = self.geo.get_coordinates(self.u.extract_adress(rjson))
                coord = json.dumps(coord) if isinstance(coord, dict) else str(coord)
                cargo_list = [c.strip() for c in rjson.get("cargo_type", "").split(",") if c.strip()]

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

                    # Salva no banco RDS
                    conn.commit()
                    print(f"Rota registrada.")
                
            print('Concluído.')

            # Fecha as conexões
            cur.close()
            release_connection(conn)

        except Exception as e:
            print("Agent Service Error:", str(e))
            raise e