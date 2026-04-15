from pydantic import BaseModel

class CargaResponse(BaseModel):
    carga: str
    total: int

class CargaListResponse(BaseModel):
    cargas: list[str]