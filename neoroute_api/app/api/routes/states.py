from fastapi import Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from fastapi import APIRouter
from app.repositories.rota_repository import RotaRepository

router = APIRouter(prefix="/states", tags=["states"])

@router.get("/top-state")
def top_state(db: Session = Depends(get_db)):
    return RotaRepository.top_state(db)