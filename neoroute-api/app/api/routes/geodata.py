from fastapi import APIRouter, Depends
from app.core.security import verify_token

from app.repositories.rota_repository import get_coordenadas

router = APIRouter()

# Consulta o banco para buscar as coordenadas geradas a partir das urls
@router.get("/list_geodata", tags=["Coordenadas"])
def coordenadas(auth: None = Depends(verify_token)):
    return get_coordenadas()