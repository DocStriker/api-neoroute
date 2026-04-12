import boto3
from botocore.exceptions import ClientError

ssm = boto3.client("ssm", "us-east-1")

def get_param(name, decrypt=True):
    try:
        return ssm.get_parameter(
            Name=name,
            WithDecryption=decrypt
        )["Parameter"]["Value"]
    except ClientError:
        raise Exception("Erro ao acessar SSM")