from psycopg2.extras import RealDictCursor
from .database import get_connection

def count_records(table_name: str):
    allowed_tables = ["rotas", "cargas"]
    
    if table_name not in allowed_tables:
        raise ValueError("Tabela não permitida")

    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(f"SELECT COUNT(*) FROM {table_name}")
    total = cur.fetchone()[0]
    cur.close()
    conn.close()
    return total

def top_carga():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""
        SELECT c.nome AS carga, COUNT(rc.rota_id) AS total
        FROM rota_cargas rc
        JOIN cargas c ON rc.carga_id = c.id
        GROUP BY c.nome
        ORDER BY total DESC
        LIMIT 1;
    """)
    result = cur.fetchone()
    cur.close()
    conn.close()
    return result

# Consulta o banco de dados para todos os tipos de cargas por quantidade de registro
def cargas():
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
def ocorrencias_por_dia():
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

