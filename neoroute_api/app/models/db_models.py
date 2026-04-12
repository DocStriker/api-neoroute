from app.repositories.database_config import get_connection, release_connection

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            
            -- tabela das rotas
            CREATE TABLE IF NOT EXISTS rotas (
                id SERIAL PRIMARY KEY,
                url VARCHAR(200) NOT NULL UNIQUE,
                state VARCHAR(2) NOT NULL,
                date DATE NOT NULL,
                coord JSONB
            );
            
            -- tabela de tipos de cargas
            CREATE TABLE IF NOT EXISTS cargas (
                id SERIAL PRIMARY KEY,
                nome VARCHAR(30) UNIQUE
            );

            -- tabela associativa (N:N)
            CREATE TABLE IF NOT EXISTS rota_cargas (
                rota_id INTEGER REFERENCES rotas(id) ON DELETE CASCADE,
                carga_id INTEGER REFERENCES cargas(id) ON DELETE CASCADE,
                PRIMARY KEY (rota_id, carga_id)
            );  
                    
            -- tabela de tipos de caches de respostas da AI
            CREATE TABLE IF NOT EXISTS process_cache (
                hash TEXT PRIMARY KEY,
                url VARCHAR(200),
                response JSONB,
                processed BOOLEAN DEFAULT FALSE
            );

            -- tabela de agent jobs
            CREATE TABLE IF NOT EXISTS jobs (
                id UUID PRIMARY KEY,
                status TEXT, -- pending, running, done, error
                created_at TIMESTAMP DEFAULT NOW()
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