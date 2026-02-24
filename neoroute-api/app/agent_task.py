#####################################################################################################
# 1. Importação de bibliotecas

import requests
from bs4 import BeautifulSoup
from geopy.geocoders import Nominatim
import psycopg2
import boto3
import time
import json
import unicodedata

from web_scrapping import Scrap # Importa a função de scraping que retorna uma lista de urls
from ai_agent import ParseToAgent # Importa a função de AI Agent para procurar com base no prompt

#####################################################################################################
# 2. Configuração de variáveis de ambiente

import boto3

ssm = boto3.client('ssm', 'us-east-1')

def get_param(name, decrypt=True):
    return ssm.get_parameter(
        Name=name,
        WithDecryption=decrypt
    )["Parameter"]["Value"]

api_token = get_param("/neoroute/api/aiagent")
scrap_df = Scrap() # Chama a função Scrap() do script 'web_scrapping.py' no qual retorna um dataframe

#####################################################################################################
# 3. Funções de utilidades

# Função para tratar dos acentos em uma string
def remove_acentos(texto):
    """entrada: 'texto' -> 'string', saída: 'string' normalizada sem acentos."""
    if not texto:
        return ""
    # Normaliza para NFD (separa caracteres + acentos)
    nfkd = unicodedata.normalize('NFD', texto)
    # Remove caracteres não-ASCII (acentos)
    return "".join([c for c in nfkd if not unicodedata.combining(c)])

# Função que gera as coordenadas de acordo o endereço passado como string
def GeoLocator(adress):
    """recebe 'adress' como string e retorna um json das coordenadas."""
    geolocator = Nominatim(user_agent="roubo_carga_scraper")

    geo_dados = []

    try:
        location = geolocator.geocode(adress)
        if location:
            geo_dados.append({
                "lat": location.latitude,
                "lng": location.longitude,
                })
    except Exception as e:
        print("Erro geocodificando:", adress, e)
    
    return geo_dados # retorno em json

# Função de chamada do agente Gemini
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

# Função na qual extrai o formato endereço do json de resposta do agente
def extract_adress(json):
    """recebe um json e retorna uma string."""
    adress = f"{json['street']}, {json['city'] + ', 'if json['city'] else ''}{json['state']}"

    return adress # Retorno em string

#####################################################################################################
# 4. Iniciando o agente

# Função principal no qual conecta ao banco de dados RDS AWS e chama o agente
def main():

    conn = psycopg2.connect(
        dbname=get_param("/neoroute/db/name"),
        user=get_param("/neoroute/db/user"),
        password=get_param("/neoroute/db/password"),
        host=get_param("/neoroute/db/host"),
        port="5432",
        connect_timeout=5
    )

    print("Conectado ao banco 'news_scrap' na porta: 5432.")

    cur = conn.cursor()

    print("Criando tabelas caso não existam... ")

    cur.execute("""
                
        -- tabela das rotas
        CREATE TABLE IF NOT EXISTS rotas (
        id SERIAL PRIMARY KEY,
        url TEXT NOT NULL,
        state TEXT,
        date DATE NOT NULL,
        coord TEXT
        );
        
        -- tabela de tipos de cargas
        CREATE TABLE IF NOT EXISTS cargas (
        id SERIAL PRIMARY KEY ,
        nome TEXT UNIQUE
        );

        -- tabela associativa (N:N)
        CREATE TABLE IF NOT EXISTS rota_cargas (
        rota_id INTEGER REFERENCES rotas(id) ON DELETE CASCADE,
        carga_id INTEGER REFERENCES cargas(id) ON DELETE CASCADE,
        PRIMARY KEY (rota_id, carga_id)
        );  
                      
        """)

    print("Tabelas criadas ou já existentes...")

    contador = 0

    for url, day in zip(scrap_df['url'], scrap_df['date']):

        cur.execute("SELECT 1 FROM rotas WHERE url = %s", (url,))
        rota_existente = cur.fetchone()

        if rota_existente:
            print(f"Url já existe no banco: {url[:10]}")
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

#####################################################################################################

if __name__ == '__main__':
    main()
