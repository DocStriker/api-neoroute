#####################################################################################################
# 1. Importação das bibliotecas

from fastapi import FastAPI, Header, HTTPException, Depends
import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi.middleware.cors import CORSMiddleware
import asyncio
#from agent_task import main
from mangum import Mangum

import boto3

ssm = boto3.client("ssm")

def get_param(name, decrypt=True):
    return ssm.get_parameter(
        Name=name,
        WithDecryption=decrypt
    )["Parameter"]["Value"]

#####################################################################################################
# 2. Configurando as variáveis de ambiente

api_token = None

def main():
    pass

def get_api_token():
    global api_token
    if api_token is None:
        api_token = get_param("/neoroute/api/token")
    return api_token

#####################################################################################################
# 3. Configurando o FastAPI

# Função para verificação do token da API
def verify_token(x_api_key: str = Header(...)):
    if x_api_key != get_api_token():
        raise HTTPException(status_code=401, detail="Unauthorized")

app = FastAPI(
    title="NeoRoute API",
    description="API para consulta de roubos de cargas, estados e coletas",
    version="1.0.0",
)

origins = [
    "*" # Front local
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,            # Quem pode acessar a API
    allow_credentials=True,
    allow_methods=["*"],              # Quais métodos (GET, POST, etc.)
    allow_headers=["*"],              # Quais cabeçalhos podem ser enviados
)

#####################################################################################################
# 4. Funções de utilidades

# Função para se conectar ao banco RDS da AWS
def get_connection():
    """conecta ao banco RDS via PostgreSQL na porta 5432."""
    return psycopg2.connect(
        dbname=get_param("/neoroute/db/name"),
        user=get_param("/neoroute/db/user"),
        password=get_param("/neoroute/db/password"),
        host=get_param("/neoroute/db/host"),
        port="5432",
        connect_timeout=5
    )

# Função para chama o agente Gemini
async def run_agent_task():
    
    main()
    # por exemplo, scrape + inserção no banco
    await asyncio.sleep(3)  # simula tempo de execução
    return {"status": "Agent executado com sucesso"}

#####################################################################################################
# 5. Criação das rotas da API

@app.get("/health", tags=["Health Check"])
def health_check():
    return {"status": "OK"}

@app.get("/token_check", tags=["Health Check"])
def token_check(auth: None = Depends(verify_token)):
    return {"status": "OK"}

# Chama o agente para executar a tarefa
@app.post("/run_agent", tags=["AI Agent"])
async def run_agent(auth: None = Depends(verify_token)):
    try:
        result = await run_agent_task()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Consulta o banco de dados para o total de registros na tabela
@app.get("/total/{table_name}", tags=["Estados"])
def total_records(table_name: str, auth: None = Depends(verify_token)):
    try:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(f"SELECT COUNT(*) AS total FROM {table_name};")
        total = cur.fetchone()["total"]
        return {"table": table_name, "total_records": total}
    except Exception as e:
        return {"error": str(e)}
    finally:
        cur.close()
        conn.close()

# Consulta o banco de dados para o estado com o maior número de registros
@app.get("/top_state/{table_name}", tags=["Estados"])
def top_state(table_name: str, auth: None = Depends(verify_token)):
    """
    Retorna o estado com maior número de registros.
    A tabela deve conter uma coluna chamada 'state'.
    """
    try:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        query = f"""
            SELECT state, COUNT(*) AS total
            FROM {table_name}
            GROUP BY state
            ORDER BY total DESC
            LIMIT 1;
        """
        cur.execute(query)
        result = cur.fetchone()
        if result:
            return {"top_state": result["state"], "total_records": result["total"]}
        else:
            return {"message": "Nenhum registro encontrado."}
    except Exception as e:
        return {"error": str(e)}
    finally:
        cur.close()
        conn.close()

# Consulta o banco de dados para retornar a lista de estados por quantidade de registros
@app.get("/states/{table_name}", tags=["Estados"])
def states(table_name: str, auth: None = Depends(verify_token)):
    try:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        query = f"""
            SELECT state, COUNT(*) AS total
            FROM {table_name}
            GROUP BY state;
        """
        cur.execute(query)
        result = cur.fetchall()
        if result:
            return result
        else:
            return {"message": "Nenhum registro encontrado."}
    except Exception as e:
        return {"error": str(e)}
    finally:
        cur.close()
        conn.close()

# Consulta o banco de dados para a carga com mais registro
@app.get("/top_carga", tags=["Cargas"])
def top_carga(auth: None = Depends(verify_token)):
    """Retorna a carga mais recorrente (com mais registros associados)."""
    try:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        query = """
            SELECT c.nome AS carga, COUNT(rc.rota_id) AS total
            FROM rota_cargas rc
            JOIN cargas c ON rc.carga_id = c.id
            GROUP BY c.nome
            ORDER BY total DESC
            LIMIT 1;
        """
        cur.execute(query)
        result = cur.fetchone()
        if result:
            return {"top_carga": result["carga"], "total_registros": result["total"]}
        else:
            return {"message": "Nenhum registro encontrado."}
    except Exception as e:
        return {"error": str(e)}
    finally:
        cur.close()
        conn.close()

# Consulta o banco de dados para todos os tipos de cargas por quantidade de registro
@app.get("/cargas", tags=["Cargas"])
def cargas(auth: None = Depends(verify_token)):
    """Retorna a carga mais recorrente (com mais registros associados)."""
    try:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        query = """
            SELECT c.nome AS carga, COUNT(rc.rota_id) AS total
            FROM rota_cargas rc
            JOIN cargas c ON rc.carga_id = c.id
            GROUP BY c.nome;
        """
        cur.execute(query)
        result = cur.fetchall()
        if result:
            return result
        else:
            return {"message": "Nenhum registro encontrado."}
    except Exception as e:
        return {"error": str(e)}
    finally:
        cur.close()
        conn.close()

# Consulta o banco de dados por ocorrências por dia
@app.get("/roubos_por_dia", tags=["Cargas"])
def ocorrencias_por_dia(auth: None = Depends(verify_token)):
    """Retorna o número de ocorrências (rotas) por dia."""
    try:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        query = """
            SELECT date, COUNT(*) AS total
            FROM rotas
            GROUP BY date
            ORDER BY date ASC;
        """
        cur.execute(query)
        results = cur.fetchall()

        # transforma para um formato fácil de usar no front
        data = [{"date": str(r["date"]), "total": r["total"]} for r in results]
        return {"ocorrencias_por_dia": data}

    except Exception as e:
        return {"error": str(e)}
    finally:
        cur.close()
        conn.close()

# Consulta o banco para buscar as coordenadas geradas a partir das urls
@app.get("/list_geodata", tags=["Coordenadas"])
def get_coordenadas(auth: None = Depends(verify_token)):
    try:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        query = """
            SELECT CONCAT(LEFT(url, 20), '...') AS url, coord FROM rotas;
            """
        
        cur.execute(query)
        results = cur.fetchall()

        return results
    
    except Exception as e:
        return {"error": str(e)}
    finally:
        cur.close()
        conn.close()

handler = Mangum(app)