from fastapi import APIRouter, Depends
from app.core.security import verify_token

from app.repositories.rota_repository import top_state, count_records, states

router = APIRouter()

@router.get("/total/{table_name}")
def get_total(table_name: str, auth: None = Depends(verify_token)):
    return count_records(table_name)

@router.get("/top_state", tags=["Estados"])
def get_top_state(auth: None = Depends(verify_token)):
    return top_state()

@router.get("/states", tags=["Estados"])
def get_states(auth: None = Depends(verify_token)):
    return states()