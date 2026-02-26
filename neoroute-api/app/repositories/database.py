import psycopg2
from app.core.config import get_param

def get_connection():
    return psycopg2.connect(
        dbname=get_param("/neoroute/db/name"),
        user=get_param("/neoroute/db/user"),
        password=get_param("/neoroute/db/password"),
        host=get_param("/neoroute/db/host"),
        port="5432",
        connect_timeout=5
    )