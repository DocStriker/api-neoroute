from sqlalchemy import Column, Integer, String, JSON, Date
from sqlalchemy.orm import relationship
from app.models.base import Base

class Rota(Base):
    __tablename__ = "rotas"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(200), nullable=False, unique=True)
    state = Column(String(2), nullable=False)
    date = Column(Date, nullable=False)  # Consider using Date type if you want to store as date
    coord = Column(JSON)  # Consider using JSON type if you want to store as JSONB

    cargas = relationship(
        "Carga",
        secondary="rota_cargas",
        back_populates="rotas"
     )