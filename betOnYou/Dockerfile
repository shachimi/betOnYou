FROM python:latest

COPY src/ /app
COPY instance /instance

WORKDIR /app

RUN pip install -r requirements.txt

ENV FLASK_APP "flaskr"
ENV FLASK_ENV "docker"

CMD ["flask", "run", "--host=0.0.0.0"]
