#!/bin/bash

set -e  # para o script se der erro

# ==============================
# CONFIGURAÇÕES
# ==============================

AWS_REGION="us-east-1"
AWS_ACCOUNT_ID="979311683347"
ECR_REPO="neoroute-lambda"
LAMBDA_NAME="api-neoroute"

# ==============================
# GERAR TAG (timestamp)
# ==============================

IMAGE_TAG=$(date +"%Y%m%d-%H%M%S")

echo "========================================="
echo "Versão gerada: $IMAGE_TAG"
echo "========================================="

# ==============================
# BUILD
# ==============================

echo "Buildando imagem..."
docker build -t $ECR_REPO:$IMAGE_TAG .

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

# ==============================
# ATUALIZAR LAMBDA
# ==============================

echo "Atualizando Lambda..."
aws lambda update-function-code \
  --function-name $LAMBDA_NAME \
  --image-uri $FULL_IMAGE_URI

echo "========================================="
echo "Deploy concluído com sucesso 🚀"
echo "Versão publicada: $IMAGE_TAG"
echo "========================================="

exit
