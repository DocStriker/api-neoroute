FROM public.ecr.aws/lambda/python:3.11

# Copia dependências
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt -t /var/task

# Copia o código
COPY main.py .

# Handler
CMD ["main.handler"]