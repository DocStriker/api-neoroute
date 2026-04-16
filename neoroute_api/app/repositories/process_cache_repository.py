from sqlalchemy.orm import Session
from app.models.cache import Cache

class ProcessCacheRepository:

    @staticmethod
    def get(hash: str, db: Session):
        return db.get(Cache, hash)

    @staticmethod
    def save(hash: str, response: dict, db: Session):
        obj = Cache(
            hash=hash,
            response=response,
            processed=True
        )
        db.merge(obj)