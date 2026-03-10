from fastapi import APIRouter, Depends
from app.core.security import verify_token

from app.repositories.carga_repository import top_carga

router = APIRouter()

@router.get("/top_carga")
def get_top_carga(auth:None = Depends(verify_token)):
    return top_carga()