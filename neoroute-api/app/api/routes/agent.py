import os
import json
import boto3
from fastapi import APIRouter, Depends
from app.core.security import verify_token
from botocore.config import Config
from app.services.agent_service import AgentService

config = Config(connect_timeout=2, read_timeout=2)

router = APIRouter()

if os.getenv("ENV") == "aws":
    sqs = boto3.client("sqs", region_name="us-east-1", config=config)
    QUEUE_URL = "https://sqs.us-east-1.amazonaws.com/979311683347/agent-queue"

@router.post("/run_agent")
def run_agent(auth: None = Depends(verify_token)):

    if os.getenv("ENV") == "aws":
        print("Recebeu requisição")

        try:

            message = {"action": "run_agent"}

            response = sqs.send_message(
                QueueUrl=QUEUE_URL,
                MessageBody=json.dumps(message)
            )

            print("Resposta SQS:", response)

        except Exception as e:
            print("ERRO:", str(e))

        print("Mensagem enviada")

        return {"status": "agent enviado para fila"}
    AgentService().run()
    