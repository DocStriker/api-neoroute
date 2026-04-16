from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.carga_service import CargaService
from app.schemas.carga_schema import CargaCount, OcurrencyByDay

router = APIRouter(prefix="/cargas", tags=["cargas"])

@router.get("/top", response_model=CargaCount)
def top_carga(db: Session = Depends(get_db)):
    result = CargaService.get_top_carga(db)
    if not result:
        return {"message": "No cargas found"}
    return result

@router.get("/", response_model=list[CargaCount])
def list_cargas(db: Session = Depends(get_db)):
    return CargaService.get_cargas(db)

@router.get("/ocurrency", response_model=list[OcurrencyByDay])
def ocurrency(db: Session = Depends(get_db)):
    return {"ocurrency_by_day": CargaService.get_ocurrency_by_day(db)}