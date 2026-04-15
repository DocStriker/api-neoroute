from sqlalchemy import Column, Integer, String
from app.core.database import Base

class Carga(Base):
    __tablename__ = "cargas"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)