FROM python:3.13.2-slim-bullseye

ENV FLASK_APP=web:app
ENV PYTHONPATH=.
ENV POETRY_VERSION=2.1.1

RUN apt update -y && \
    DEBIAN_FRONTEND=noninteractive apt install -y vim-tiny jq curl unzip gcc libpq-dev wget && \
    apt clean -y

WORKDIR /usr/src/app

RUN pip3 install "poetry==$POETRY_VERSION" --no-cache-dir && \
    poetry config virtualenvs.create false && \
    poetry config virtualenvs.in-project false

COPY pyproject.toml poetry.lock*  /usr/src/app/

RUN poetry install --no-interaction --no-root --no-ansi --no-cache

# only files explicitly configured in `.dockerignore` will be copied into the container
COPY . .

EXPOSE 5000

CMD ["gunicorn", "--keep-alive", "65", "--worker-class", "gevent", "-w", "4", "-b", "0.0.0.0:5000", "web:app"]
