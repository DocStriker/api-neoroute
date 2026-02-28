from fastapi import Header, HTTPException
from app.core.config import get_param

_api_token = None

def get_api_token():
    global _api_token
    if _api_token is None:
        _api_token = get_param("/neoroute/api/token")
    return _api_token

def verify_token(x_api_key: str = Header(...)):
    if x_api_key != get_api_token():
        raise HTTPException(status_code=401, detail="Unauthorized")