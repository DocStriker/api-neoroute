from fastapi import APIRouter
from fastapi import HTTPException
from app.repositories.database_config import get_connection, release_connection

router = APIRouter()

@router.get("/status/{job_id}")
def get_status(job_id: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT status FROM jobs WHERE id = %s", (job_id,))
    result = cur.fetchone()
    cur.close()
    release_connection(conn)

    if not result:
        raise HTTPException(404, "Job not found")

    return {"status": result[0]}