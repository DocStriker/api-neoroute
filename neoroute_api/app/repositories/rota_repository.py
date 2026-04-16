from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.rotas import Rota
from app.models.carga import Carga
from app.models.association import rota_cargas

class RotaRepository:
    @staticmethod
    def count_records(db: Session, table: str) -> int:
        allowed = {
            "rotas": Rota,
            "cargas": Carga
        }

        model = allowed.get(table)

        if not model:
            raise ValueError("Tabela não permitida")

        return db.query(func.count(model.id)).scalar()

    @staticmethod
    def top_state(db: Session):
        result = (
            db.query(
                Rota.state,
                func.count(Rota.id).label("total")
            )
            .group_by(Rota.state)
            .order_by(func.count(Rota.id).desc())
            .limit(1)
            .first()
        )

        if not result:
            return None

        return {
            "top_state": result.state,
            "total_records": result.total
        }


    @staticmethod
    def states(db: Session):
        results = (
            db.query(
                Rota.state,
                func.count(Rota.id).label("total")
            )
            .group_by(Rota.state)
            .all()
        )

        return [
            {"state": r.state, "total": r.total}
            for r in results
        ]


    @staticmethod
    def get_coordenadas(db: Session):
        results = (
            db.query(
                Rota.url,
                Rota.coord
            )
            .all()
        )

        return [
            {
                "url": f"{r.url[:20]}..." if r.url else None,
                "coord": r.coord
            }
            for r in results
        ]
    
    @staticmethod
    def create(db, **kwargs):
        rota = Rota(**kwargs)
        db.add(rota)
        db.flush()
        return rota

    @staticmethod
    def link_carga(db, rota_id, carga_id):
        db.execute(
            rota_cargas.insert().values(
                rota_id=rota_id,
                carga_id=carga_id
            )
        )