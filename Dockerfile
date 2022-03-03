FROM tiangolo/uvicorn-gunicorn:python3.9-alpine3.14

RUN pip install --upgrade pip

WORKDIR /app

COPY requirements.txt ./

RUN pip install -r requirements.txt

COPY . .
