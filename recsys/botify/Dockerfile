FROM python:3.7

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY botify ./botify

COPY data ./data

ENV PYTHONPATH "${PYTHONPATH}:/app"