from app.repositories.database import get_connection, release_connection


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    try:
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
                id SERIAL PRIMARY KEY,
                nome TEXT UNIQUE
            );

            -- tabela associativa (N:N)
            CREATE TABLE IF NOT EXISTS rota_cargas (
                rota_id INTEGER REFERENCES rotas(id) ON DELETE CASCADE,
                carga_id INTEGER REFERENCES cargas(id) ON DELETE CASCADE,
                PRIMARY KEY (rota_id, carga_id)
            );  
                    
            -- tabela de tipos de caches de respostas da AI
            CREATE TABLE IF NOT EXISTS ai_cache (
                hash TEXT PRIMARY KEY,
                response TEXT
            );        
        """)

        conn.commit()

    except Exception as e:
        conn.rollback()
        raise e

    finally:
        cur.close()
        release_connection(conn)

    return True