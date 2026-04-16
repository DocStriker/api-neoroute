from sqlalchemy import Column, CHAR, String, JSON, Boolean
from app.core.database import Base

class Cache(Base):
    __tablename__ = "process_cache"

    hash = Column(CHAR(64), primary_key=True, index=True)
    url = Column(String(200))
    response = Column(JSON)
    processed = Column(Boolean, default=False)