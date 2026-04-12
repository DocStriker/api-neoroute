import sys
import time
import boto3

REGION = "us-east-1"
DB_INSTANCE_ID = "neoroute-db-instance"

rds = boto3.client("rds", region_name=REGION)


def get_status():
    response = rds.describe_db_instances(
        DBInstanceIdentifier=DB_INSTANCE_ID
    )
    return response["DBInstances"][0]["DBInstanceStatus"]


def start_db():
    status = get_status()
    if status != "stopped":
        print(f"RDS não está parado (status atual: {status})")
        return

    rds.start_db_instance(DBInstanceIdentifier=DB_INSTANCE_ID)
    print("⏳ Iniciando RDS...")


def stop_db():
    status = get_status()
    if status != "available":
        print(f"RDS não está disponível para parar (status atual: {status})")
        return

    rds.stop_db_instance(DBInstanceIdentifier=DB_INSTANCE_ID)
    print("⏳ Parando RDS...")


def wait_until_available():
    print("⏳ Aguardando RDS ficar disponível...")
    while True:
        status = get_status()
        print(f"Status atual: {status}")
        if status == "available":
            print("✅ RDS pronto para uso")
            break
        if status == "stopped":
            print("✅ RDS parado")
            break
        time.sleep(20)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python rds_control.py [start|stop|status|wait]")
        sys.exit(1)

    command = sys.argv[1]

    if command == "start":
        start_db()
    elif command == "stop":
        stop_db()
    elif command == "status":
        print(f"Status atual: {get_status()}")
    elif command == "wait":
        wait_until_available()
    else:
        print("Comando inválido")
