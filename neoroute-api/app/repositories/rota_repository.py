from .database import get_connection

def count_records(table_name: str):
    allowed_tables = ["rotas", "cargas"]
    
    if table_name not in allowed_tables:
        raise ValueError("Tabela não permitida")

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT COUNT(*) FROM {table_name}")
    total = cur.fetchone()[0]
    cur.close()
    conn.close()
    return total