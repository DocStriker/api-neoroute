from sqlalchemy import Column, Integer, String
from app.core.database import Base
from sqlalchemy import Table, ForeignKey

rota_cargas = Table(
    "rota_cargas",
    Base.metadata,
    Column("rota_id", Integer, ForeignKey("rotas.id", ondelete="CASCADE"), primary_key=True),
    Column("carga_id", Integer, ForeignKey("cargas.id", ondelete="CASCADE"), primary_key=True),
)