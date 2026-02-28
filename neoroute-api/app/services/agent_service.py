import time

from app.services.scraping_service import ScrapingService
from app.services.ai_service import AIService
from app.services.geolocation_service import GeolocationService
from app.utils.utils import Utils
from app.repositories.database import get_connection
from app.models.db_models import init_db

class AgentService:

    def Agent(url, api_token):
        """recebe uma 'url' + 'api_token' para o agente no qual retorna um json da resposta."""
        try:
            html = requests.get(url, timeout=6).text  # timeout em segundos
            soup = BeautifulSoup(html, "html.parser")

            texto = " ".join([p.get_text() for p in soup.find_all("p")])

            response = ParseToAgent(texto, api_token)

        except requests.exceptions.ConnectTimeout:
            print(f"Tempo esgotado para {url[:10]}")
            response = None
        except requests.exceptions.RequestException as e:
            print(f"Erro ao acessar {url[:10]}: {e}")
            response = None

        return response # Resposta em JSON.

    def __init__(self):
        self.scraper = ScrapingService()
        self.ai = AIService()
        self.geo = GeolocationService()

    def run(self):
        df = self.scraper.fetch_gdelt()
        init_db()

        conn = get_connection()
        cur = conn.cursor()

        contador = 0

        for _, row in df.iterrows():
            # aqui entraria persistência via repository
            print("Processando:", row["url"])

            cur.execute("SELECT 1 FROM rotas WHERE url = %s", (row["url"],))
            rota_existente = cur.fetchone()

            if rota_existente:
                print(f"Url já existe no banco: {row["url"][:10]}")
                continue

            contador += 1

            if contador % 10 == 0:
                print("\n Atingido 10 requisições. Aguardando 60 segundos...")
                time.sleep(60)  # pausa de 1 minuto
                print("Retomando execução...\n")

            rjson = Agent(url, api_token)

            if isinstance(rjson, list) and len(rjson) > 0:
                rjson = [rjson[0]]

            elif isinstance(rjson, dict):
                rjson = [rjson]

            else:
                continue  # nenhum dado válido

            for r in rjson:

                state = r.get("state", None)
                coord = GeoLocator(extract_adress(r))
                coord = json.dumps(coord) if isinstance(coord, dict) else str(coord)
                cargo_list = [c.strip() for c in r.get("cargo_type", "").split(",") if c.strip()]

                # Insere rota
                cur.execute(
                    "INSERT INTO rotas (url, state, date, coord) VALUES (%s, %s, %s, %s) RETURNING id;",
                    (url, state, day, coord)
                )
                rota_id = cur.fetchone()[0]

                # Insere cada carga e vincula à rota
                # Para cada carga
                for cargo in cargo_list:
                    cargo = remove_acentos(cargo.strip().lower())  # normaliza (evita duplicados tipo "Combustível" vs "combustivel")

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
        conn.close()