FROM python:latest

COPY src/ /app
COPY instance /app/instance

WORKDIR /app

RUN pip install -r requirements.txt

ENV FLASK_APP "flaskr"
ENV FLASK_ENV "docker"

