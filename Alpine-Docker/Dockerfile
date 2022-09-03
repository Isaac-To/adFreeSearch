####################################################################################################
## Builder image
####################################################################################################
FROM python:3.10.6-alpine3.16 AS builder

RUN apk add --no-cache \
    ca-certificates \
    build-base \
    curl \
    linux-headers 

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
RUN python -m pip install --upgrade pip setuptools
RUN curl -sSL https://install.python-poetry.org | python -
ENV PATH="${PATH}:/root/.local/bin"

WORKDIR /AdFreeSearch

COPY /pyproject.toml /AdFreeSearch/
COPY /poetry.lock /AdFreeSearch/

RUN poetry export -f requirements.txt --output requirements.txt --without-hashes \
    && pip wheel --wheel-dir=/AdFreeSearch/wheels -r requirements.txt

####################################################################################################
## Final image
####################################################################################################
FROM python:3.10.6-alpine3.16
RUN apk add --no-cache \
    ca-certificates \
    tini \
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

ENTRYPOINT ["/sbin/tini", "--"]

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "5", "main:app"]

STOPSIGNAL SIGTERM

LABEL org.opencontainers.image.title="adFreeSearch"
LABEL org.opencontainers.image.description="A private, security oriented search engine"
LABEL org.opencontainers.image.licenses=""
LABEL org.opencontainers.image.source="https://github.com/Isaac-To/adFreeSearch"
