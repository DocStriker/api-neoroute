#!/bin/bash

set -e  # para o script se der erro

# ==============================
# CONFIGURAÇÕES
# ==============================

AWS_REGION="us-east-1"
AWS_ACCOUNT_ID="979311683347"
ECR_REPO="agent-worker"

# ==============================
# GERAR TAG (timestamp)
# ==============================

IMAGE_TAG="latest"

echo "========================================="
echo "Versão gerada: $IMAGE_TAG"
echo "========================================="

# ==============================
# BUILD
# ==============================

echo "Buildando imagem..."
docker build -f Dockerfile.worker -t $ECR_REPO:$IMAGE_TAG .

# ==============================
# LOGIN ECR
# ==============================

echo "Logando no ECR..."
aws ecr get-login-password --region $AWS_REGION \
| docker login --username AWS --password-stdin \
$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

# ==============================
# TAG PARA ECR
# ==============================

FULL_IMAGE_URI="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO:$IMAGE_TAG"

docker tag $ECR_REPO:$IMAGE_TAG $FULL_IMAGE_URI

# ==============================
# PUSH
# ==============================

echo "Enviando imagem para ECR..."
docker push $FULL_IMAGE_URI