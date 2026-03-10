from fastapi import APIRouter, Depends
from app.core.security import verify_token

from app.repositories.carga_repository import top_carga, ocorrencias_por_dia, cargas, count_records

router = APIRouter()

@router.get("/total/{table_name}")
def get_total(table_name: str, auth: None = Depends(verify_token)):
    return count_records(table_name)

@router.get("/top_carga")
def get_top_carga(auth:None = Depends(verify_token)):
    return top_carga()

@router.get("/cargas", tags=["Cargas"])
def get_cargas(auth: None = Depends(verify_token)):
    return cargas()

@router.get("/roubos_por_dia", tags=["Cargas"])
def get_ocorrencias(auth: None = Depends(verify_token)):
    return ocorrencias_por_dia()