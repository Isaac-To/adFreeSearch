###################################################################################################
## Builder image
####################################################################################################
FROM python:3.10.6-slim-bullseye AS builder
ENV DEBIAN_FRONTEND=noninteractive 
RUN apt update \
    && apt install -y --no-install-recommends \
    build-essential \
    curl \
    ca-certificates

# Ad Poetry Locally
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
RUN python -m pip install --upgrade pip setuptools
RUN curl -sSL https://install.python-poetry.org | python -
ENV PATH="${PATH}:/root/.local/bin"

WORKDIR /AdFreeSearch

COPY /pyproject.toml /AdFreeSearch/
COPY /poetry.lock /AdFreeSearch/

# Create dependency wheels
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes \
    && pip wheel --wheel-dir=/AdFreeSearch/wheels -r requirements.txt

####################################################################################################
## Final image
####################################################################################################
FROM python:3.10.6-slim-bullseye
RUN apt update \
    && apt install -y --no-install-recommends \
    tini \
    ca-certificates \
    bash

WORKDIR /AdFreeSearch
COPY /app/main.py /AdFreeSearch/
COPY /app/css /AdFreeSearch/css
COPY /app/templates /AdFreeSearch/templates
COPY /app/static /AdFreeSearch/static
COPY /app/websources /AdFreeSearch/websources

COPY --from=builder /AdFreeSearch/wheels /AdFreeSearch/wheels
COPY --from=builder /AdFreeSearch/requirements.txt /AdFreeSearch/requirements.txt

RUN adduser --disabled-password --gecos "" adfreesearch \
    && chown -R adfreesearch:adfreesearch /AdFreeSearch 

USER adfreesearch

ENV PATH="${PATH}:/home/adfreesearch/.local/bin"
ENV PYTHONDONTWRITEBYTECODE 1

RUN pip install --user --no-index --find-links=/AdFreeSearch/wheels -r requirements.txt

EXPOSE 5000

ENTRYPOINT ["/usr/bin/tini", "--"]

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "5", "main:app"]

STOPSIGNAL SIGTERM

LABEL org.opencontainers.image.title="adFreeSearch"
LABEL org.opencontainers.image.description="A private, security oriented search engine"
LABEL org.opencontainers.image.licenses=""
LABEL org.opencontainers.image.source="https://github.com/Isaac-To/adFreeSearch"
