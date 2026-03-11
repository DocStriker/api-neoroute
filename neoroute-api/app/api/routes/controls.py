from fastapi import APIRouter, Depends
from app.core.security import verify_token

from app.services.database_service import get_status, start_db, stop_db

router = APIRouter()

@router.get("/db_status")
def get_db_status(auth: None = Depends(verify_token)):
    return get_status()

@router.post("/start_db")
def init_instance(auth: None = Depends(verify_token)):
    return start_db()

@router.post("/stop_db")
def stop_instance(auth: None = Depends(verify_token)):
    return stop_db()