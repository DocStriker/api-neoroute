from sqlalchemy.orm import Session
from app.models.job import Job
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