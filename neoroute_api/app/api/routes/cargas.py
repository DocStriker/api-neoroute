from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.carga_service import CargaService

router = APIRouter(prefix="/cargas", tags=["cargas"])

@router.get("/top")
def top_carga(db: Session = Depends(get_db)):
    result = CargaService.get_top_carga(db)
    if not result:
        return {"message": "No cargas found"}
    return result

@router.get("/")
def list_cargas(db: Session = Depends(get_db)):
    return CargaService.get_cargas(db)

@router.get("/ocurrency")
def ocurrency(db: Session = Depends(get_db)):
    return {"ocurrency_by_day": CargaService.get_ocurrency_by_day(db)}