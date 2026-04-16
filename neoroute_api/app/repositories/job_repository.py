from sqlalchemy.orm import Session
from app.models.job import Job
from datetime import datetime

class JobRepository:

    @staticmethod
    def update_status(db: Session, job_id: str, status: str):
        job = db.query(Job).filter(Job.id == job_id).first()

        if not job:
            raise Exception("Job not found")

        job.status = status
        job.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(job)

        return job