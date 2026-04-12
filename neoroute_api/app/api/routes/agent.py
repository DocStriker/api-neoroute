import os
import json
import boto3
import uuid

from fastapi import APIRouter, Depends, BackgroundTasks
from app.core.security import verify_token
from botocore.config import Config
from app.services.agent_service import AgentService
from app.repositories.database_config import get_connection, release_connection

config = Config(connect_timeout=2, read_timeout=2)

router = APIRouter()

if os.getenv("ENV") == "aws":
    sqs = boto3.client("sqs", region_name="us-east-1", config=config)
    QUEUE_URL = "https://sqs.us-east-1.amazonaws.com/979311683347/agent-queue"

@router.post("/run_agent")
def run_agent(background_tasks: BackgroundTasks,auth: None = Depends(verify_token)):
    agent= AgentService()
    job_id = str(uuid.uuid4())

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO jobs (id, status) VALUES (%s, %s)",
        (job_id, "pending")
    )
    conn.commit()

    cur.close()
    release_connection(conn)

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
    
    background_tasks.add_task(agent.run, job_id)
    return {"status": "agent started in background", "job_id": job_id}