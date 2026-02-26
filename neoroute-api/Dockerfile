FROM public.ecr.aws/lambda/python:3.11

# Copia dependências
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

# Copia o código
COPY app ${LAMBDA_TASK_ROOT}/app

# Handler
CMD ["app.main.handler"]