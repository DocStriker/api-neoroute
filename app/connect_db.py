import psycopg2
import boto3
from dotenv import load_dotenv
import os

load_dotenv()

password = os.getenv("RDS_PASS")

conn = None
try:
    conn = psycopg2.connect(
        host='neoroute-db-instance.cwn2ecuw8v62.us-east-1.rds.amazonaws.com',
        port=5432,
        database='neoroutedb',
        user='gallifrey',
        password=password,
    )
    cur = conn.cursor()
    cur.execute('SELECT version();')
    print(cur.fetchone()[0])
    cur.close()
except Exception as e:
    print(f"Database error: {e}")
    raise
finally:
    if conn:
        conn.close()