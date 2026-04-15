from sqlalchemy.orm import Session
from sqlalchemy import func, text
from app.models.carga import Carga

class CargaRepository:
    @staticmethod
    def top_carga(db: Session):
        result = (
            db.query(Carga.name.label("carga"), func.count().label("total"))
            .join(text("rota_cargas rc ON rc.carga_id = cargas.id"))
            .group_by(Carga.name)
            .order_by(func.count().desc())
            .limit(1)
            .first()
        )
        return result
    
    @staticmethod
    def list_cargas(db: Session):
        result = (
            db.query(Carga.name.label("carga"), func.count().label("total"))
            .join(text("rota_cargas rc ON rc.carga_id = cargas.id"))
            .group_by(Carga.name)
            .all()
        )
        return result
    
    @staticmethod
    def ocurrency_by_day(db: Session):
        query = text("""
            SELECT date, COUNT(*) AS total
            FROM rotas
            GROUP BY date
            ORDER BY date ASC;
        """)
        result = db.execute(query).fetchall()
        return result
