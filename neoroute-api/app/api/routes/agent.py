from fastapi import APIRouter, Depends
from app.core.security import verify_token
from app.services.agent_service import AgentService

router = APIRouter()

@router.post("/run_agent")
def run_agent(auth: None = Depends(verify_token)):
    AgentService().run()
    return {"status": "executado"}