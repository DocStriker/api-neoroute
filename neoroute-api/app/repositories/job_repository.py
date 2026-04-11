import logging
from app.repositories.database_config import get_connection, release_connection

logger = logging.getLogger(__name__)

def update_job(job_id: str, status: str):
    conn = None
    cur = None

    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            """
            UPDATE jobs
            SET status = %s
            WHERE id = %s
            """,
            (status, job_id)
        )

        conn.commit()

        logger.info(
            "Job %s updated to status: %s",
            job_id,
            status
        )

    except Exception as e:
        if conn:
            conn.rollback()

        logger.error(
            "Failed to update job %s: %s",
            job_id,
            str(e)
        )

    finally:
        if cur:
            cur.close()
        if conn:
            release_connection(conn)
