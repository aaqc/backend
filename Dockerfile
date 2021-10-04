FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

# Dependencies 
COPY requirements.txt .
RUN python3 -m pip install -r requirements.txt

# Code
COPY ./app /app
