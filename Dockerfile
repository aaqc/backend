FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

WORKDIR /src

COPY ./app /app

