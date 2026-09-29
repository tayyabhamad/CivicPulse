# syntax=docker/dockerfile:1
FROM python:3.12.8-slim AS builder

ENV VIRTUAL_ENV=/opt/venv \
    PATH="/opt/venv/bin:$PATH" \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

RUN python -m venv "$VIRTUAL_ENV"
WORKDIR /build
COPY pyproject.toml ./
COPY app ./app
COPY scripts ./scripts
RUN pip install --upgrade pip==24.3.1 && pip install .

FROM python:3.12.8-slim AS runtime

ENV VIRTUAL_ENV=/opt/venv \
    PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

RUN groupadd --gid 10001 civicpulse \
    && useradd --uid 10001 --gid civicpulse --create-home --shell /usr/sbin/nologin civicpulse

WORKDIR /app
COPY --from=builder --chown=civicpulse:civicpulse /opt/venv /opt/venv
COPY --chown=civicpulse:civicpulse alembic.ini ./
COPY --chown=civicpulse:civicpulse alembic ./alembic
COPY --chown=civicpulse:civicpulse app ./app
COPY --chown=civicpulse:civicpulse scripts ./scripts

USER civicpulse
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
