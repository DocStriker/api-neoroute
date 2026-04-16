from pydantic import BaseModel
from datetime import date

class CargaCount(BaseModel):
    carga: str
    total: int

    class Config:
        from_attributes = True

class OcurrencyByDay(BaseModel):
    date: date
    total: int

    class Config:
        from_attributes = True