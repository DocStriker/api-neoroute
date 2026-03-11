import boto3

REGION = "us-east-1"
DB_INSTANCE_ID = "neoroute-db-instance"

rds = boto3.client("rds", region_name=REGION)


def get_status():
    try:
        response = rds.describe_db_instances(
            DBInstanceIdentifier=DB_INSTANCE_ID
        )
        return response["DBInstances"][0]["DBInstanceStatus"]
    except Exception as e:
        return {"error": str(e)}


def start_db():
    status = get_status()
    if status != "stopped":
        print(f"RDS não está parado (status atual: {status})")
        return {"response":"200", "message":f"Instância não está parada, status = {status}"}

    rds.start_db_instance(DBInstanceIdentifier=DB_INSTANCE_ID)
    print("Iniciando RDS...")
    return {"response":"200", "message":"Iniciando Instância..."}


def stop_db():
    status = get_status()
    if status != "available":
        print(f"RDS não está disponível para parar (status atual: {status})")
        return {"response":"200", "message":f"Instância indisponível para parar, status = {status}"}

    rds.stop_db_instance(DBInstanceIdentifier=DB_INSTANCE_ID)
    print("Parando RDS...")
    return {"response":"200", "message":"Parando Instância..."}
