from app.repositories.database import get_connection

def init_db():
    conn = get_connection()
    cur = conn.cursor()
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
    cur.close()
    conn.close()