from psycopg2.extras import RealDictCursor
from .database_config import get_connection, release_connection

def count_records(table_name: str):
    allowed_tables = ["rotas", "cargas"]
    
    if table_name not in allowed_tables:
        raise ValueError("Tabela não permitida")

    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(f"SELECT COUNT(*) FROM {table_name}")
    total = cur.fetchone()
    cur.close()
    release_connection(conn)
    return total

def top_state():
    """
    Retorna o estado com maior número de registros.
    A tabela deve conter uma coluna chamada 'state'.
    """
    try:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        query = f"""
            SELECT state, COUNT(*) AS total
            FROM rotas
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
        release_connection(conn)

def states():

    try:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        query = f"""
            SELECT state, COUNT(*) AS total
            FROM rotas
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
        release_connection(conn)

def get_coordenadas():
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
        release_connection(conn)