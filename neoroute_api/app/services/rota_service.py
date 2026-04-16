from sqlalchemy.orm import Session
from app.repositories.rota_repository import RotaRepository

class RotaService:

    @staticmethod
    def get_top_state(db: Session):
        return RotaRepository.top_state(db)