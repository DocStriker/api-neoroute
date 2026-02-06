FROM public.ecr.aws/lambda/python:3.10

# Copia dependências
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copia o código
COPY . .

# Handler do Lambda
CMD ["main.handler"]
