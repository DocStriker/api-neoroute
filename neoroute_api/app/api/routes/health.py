import os
from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
def health():
    return {"status": "OK", "env": os.getenv("ENV")}