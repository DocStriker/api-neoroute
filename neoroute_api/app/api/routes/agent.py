from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, get_db
from app.core.security import verify_token
from app.services.agent_service import AgentService
from app.services.job_service import JobService

router = APIRouter()

@router.post("/run_agent")
def run_agent(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    auth: None = Depends(verify_token)
):
    job_id = JobService.create_job(db)

    def task():
        db = SessionLocal()
        try:
            agent = AgentService()
            agent.run(job_id, db)
        finally:
            db.close()

    background_tasks.add_task(task)

    return {
        "status": "agent started in background",
        "job_id": job_id
    }
