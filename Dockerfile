FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

# Dependencies 
COPY requirements.txt .
RUN python3 -m pip install -r requirements.txt
RUN apt-get update
RUN apt-get install -y python3-dev default-libmysqlclient-dev build-essential

# Code
COPY ./app /app
