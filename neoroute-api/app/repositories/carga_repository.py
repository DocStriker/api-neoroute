from psycopg2.extras import RealDictCursor
from .database import get_connection

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