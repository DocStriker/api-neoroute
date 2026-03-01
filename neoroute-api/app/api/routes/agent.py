import json
import boto3
from fastapi import APIRouter, Depends
from app.core.security import verify_token

router = APIRouter()

sqs = boto3.client("sqs", region_name="us-east-1")
QUEUE_URL = "https://sqs.us-east-1.amazonaws.com/979311683347/agent-queue"

@router.post("/run_agent")
def run_agent(auth: None = Depends(verify_token)):

    message = {
        "action": "run_agent"
    }

    sqs.send_message(
        QueueUrl=QUEUE_URL,
        MessageBody=json.dumps(message)
    )

    return {"status": "agent enviado para fila"}