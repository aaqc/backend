FROM python:3.8

COPY ./src /app
COPY ./requirements.txt /app

RUN pip3 install -r /app/requirements.txt

CMD ["uvicorn", "src.main:app", "--reload", "--port", "8000"]