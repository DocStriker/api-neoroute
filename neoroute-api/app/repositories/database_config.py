import os
from psycopg2 import pool
from app.core.ssm_config import get_param

# Carrega .env apenas fora de produção
if os.getenv("ENV") == "local":
    from dotenv import load_dotenv
    load_dotenv()

def build_db_config():
    """
    Centraliza a construção da conexão para todos os ambientes
    """

    if os.getenv("ENV") == "aws":
        return {
            "dbname": get_param("/neoroute/db/name"),
            "user": get_param("/neoroute/db/user"),
            "password": get_param("/neoroute/db/password"),
            "host": get_param("/neoroute/db/host"),
            "port": "5432",
            "sslmode": "require",
            "connect_timeout": 5,
        }

    # Render / local via DATABASE_URL
    return {
        "dsn": os.getenv("DATABASE_URL"),
    }


# Inicializa pool uma única vez
db_config = build_db_config()

connection_pool = pool.SimpleConnectionPool(
    1,
    10,
    **db_config
)


def get_connection():
    return connection_pool.getconn()


def release_connection(conn):
    connection_pool.putconn(conn)