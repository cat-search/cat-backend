# Change to python:3.12-slim later
FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive \
    LC_ALL=C.UTF-8 \
    LANG=C.UTF-8 \
    PGTZ=UTC \
    # For system-wide poetry installation. Allows pip to remove system python packages
    PIP_BREAK_SYSTEM_PACKAGES=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
      iputils-ping \
      telnet \
      curl \
      wget \
      python3.12 \
      python3.12-dev \
      python3-pip \
      libxml2-dev \
      libxslt-dev \
      libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install and allow poetry to install packages system-wide
RUN pip3 --no-cache-dir install poetry --break-system-packages
# RUN curl -sSL https://install.python-poetry.org | python3 -
# ENV PATH="/root/.local/bin:$PATH"

RUN mkdir -p                    /opt/catsearch/cat-backend

COPY ./pyproject.toml           /opt/catsearch/cat-backend
COPY ./poetry.lock              /opt/catsearch/cat-backend
COPY ./alembic.ini              /opt/catsearch/cat-backend

WORKDIR                         /opt/catsearch/cat-backend

# Install packages system-wide
RUN poetry config virtualenvs.create false
RUN poetry install --no-root --no-interaction --no-ansi --compile --only main

ENV PYTHONPATH="${PYTHONPATH}:/opt/catsearch/cat-backend"

COPY ./entrypoint.sh            /opt/catsearch/cat-backend/entrypoint.sh
RUN chmod +x                    /opt/catsearch/cat-backend/entrypoint.sh
ENTRYPOINT ["/opt/catsearch/cat-backend/entrypoint.sh"]

COPY ./src/                     /opt/catsearch/cat-backend/src

CMD ["uvicorn", "main:app", "--port", "80", "--workers", "${WORKERS:-1}"]
