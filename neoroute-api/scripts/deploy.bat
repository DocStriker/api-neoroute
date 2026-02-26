@echo off
setlocal EnableDelayedExpansion

REM ==============================
REM CONFIGURE AQUI
REM ==============================

set AWS_REGION=us-east-1
set AWS_ACCOUNT_ID=979311683347
set ECR_REPO=neoroute-lambda
set LAMBDA_NAME=api-neoroute
set IMAGE_TAG=latest

REM ==============================
REM GERAR TAG COM TIMESTAMP
REM ==============================

for /f %%i in ('powershell -NoProfile -Command "Get-Date -Format yyyyMMdd-HHmmss"') do set IMAGE_TAG=%%i

echo.
echo ===== Versao gerada: %IMAGE_TAG% =====

REM ==============================
REM BUILD
REM ==============================

echo.
echo ===== Buildando imagem Docker =====
docker build --no-cache -t %ECR_REPO% .

IF %ERRORLEVEL% NEQ 0 (
    echo Erro no build.
    exit /b %ERRORLEVEL%
)

REM ==============================
REM LOGIN NO ECR
REM ==============================

echo.
echo ===== Logando no ECR =====
aws ecr get-login-password --region %AWS_REGION% | docker login --username AWS --password-stdin %AWS_ACCOUNT_ID%.dkr.ecr.%AWS_REGION%.amazonaws.com

IF %ERRORLEVEL% NEQ 0 (
    echo Erro no login do ECR.
    exit /b %ERRORLEVEL%
)

REM ==============================
REM TAG DA IMAGEM
REM ==============================

echo.
echo ===== Tagueando imagem =====
docker tag %ECR_REPO%:latest %AWS_ACCOUNT_ID%.dkr.ecr.%AWS_REGION%.amazonaws.com/%ECR_REPO%:%IMAGE_TAG%

REM ==============================
REM PUSH PARA O ECR
REM ==============================

echo.
echo ===== Enviando imagem para ECR =====
docker push %AWS_ACCOUNT_ID%.dkr.ecr.%AWS_REGION%.amazonaws.com/%ECR_REPO%:%IMAGE_TAG%

IF %ERRORLEVEL% NEQ 0 (
    echo Erro no push.
    exit /b %ERRORLEVEL%
)

REM ==============================
REM ATUALIZA LAMBDA
REM ==============================

echo.
echo ===== Atualizando Lambda =====
aws lambda update-function-code ^
    --function-name %LAMBDA_NAME% ^
    --image-uri %AWS_ACCOUNT_ID%.dkr.ecr.%AWS_REGION%.amazonaws.com/%ECR_REPO%:%IMAGE_TAG%

IF %ERRORLEVEL% NEQ 0 (
    echo Erro ao atualizar Lambda.
    exit /b %ERRORLEVEL%
)

echo.
echo ===== Deploy concluido com sucesso! =====
echo Versao publicada: %IMAGE_TAG%
echo.

endlocal
pause
