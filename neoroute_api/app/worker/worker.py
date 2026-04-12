from app.services.agent_service import AgentService
import time
import os

print("TASK STARTED")
print("Timestamp:", time.time())
print("Container hostname:", os.environ.get("HOSTNAME"))

if __name__ == "__main__":
    AgentService().run()