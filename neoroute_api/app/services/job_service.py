from sqlalchemy.orm import Session
from app.models.job import Job
from app.core.database import get_db
from app.repositories.job_repository import JobRepository
import uuid

class JobService:

    @staticmethod
    def create_job(db: Session) -> str:
        job = Job(
            id=uuid.uuid4(),
            status="pending"
        )

        db.add(job)
        db.commit()
        db.refresh(job)

        return str(job.id)

    @staticmethod
    def update_job(job_id: str, status: str):
        db = next(get_db())

        try:
            JobRepository.update_status(db, job_id, status)
        finally:
            db.close()