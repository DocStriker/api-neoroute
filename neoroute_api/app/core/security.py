import os
from fastapi import Header, HTTPException
from app.core.ssm_config import get_param
from dotenv import load_dotenv
load_dotenv()

_api_token = None

def get_api_token():
    global _api_token
    if _api_token is None:
        if os.getenv("ENV") == "aws":
            _api_token = get_param("/neoroute/api/token")
        _api_token = os.getenv("API_TOKEN")
    return _api_token

def verify_token(x_api_key: str = Header(...)):
    if x_api_key != get_api_token():
        raise HTTPException(status_code=401, detail="Unauthorized")