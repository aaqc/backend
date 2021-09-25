FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

COPY requirements.txt .

RUN python3 -m pip install -r requirements.txt

COPY ./app /app

