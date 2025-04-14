FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
  && apt-get install python3-pip -y \
  && apt-get install libxml2-dev -y \
  && apt-get install libxslt-dev -y \
  && apt-get install libpq-dev -y

ENV LC_ALL C.UTF-8
ENV LANG   C.UTF-8

# -- Install Poetry:
RUN pip3 --no-cache-dir install poetry

RUN  mkdir -p                          /opt/catsearch/cat-backend
COPY ./pyproject.toml                  /opt/catsearch/cat-backend
COPY ./poetry.lock                     /opt/catsearch/cat-backend
COPY ./alembic.ini                     /opt/catsearch/cat-backend

WORKDIR                                /opt/catsearch/cat-backend

ARG PIP_DEFAULT_TIMEOUT=90

RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction --no-ansi --compile --only main


COPY ./app/                          /opt/catsearch/cat-backend/app
COPY ./auth/                         /opt/catsearch/cat-backend/auth
COPY ./config/                       /opt/catsearch/cat-backend/config
COPY ./migrations/                   /opt/catsearch/cat-backend/migrations
COPY ./entrypoint.sh                 /opt/catsearch/cat-backend/entrypoint.sh
COPY config/supervisord.conf         /etc/supervisor/supervisord.conf

RUN chmod +x                         /opt/catsearch/cat-backend/entrypoint.sh

ENV PYTHONPATH "${PYTHONPATH}:/opt/catsearch/cat-backend"

ENTRYPOINT ["/opt/catsearch/cat-backend/entrypoint.sh"]

VOLUME                                    /var/log
EXPOSE 8080


CMD ["/usr/local/bin/supervisord", "-n", "-c", "/etc/supervisor/supervisord.conf"]