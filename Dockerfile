# ---- Build stage ----
FROM python:3.12-slim AS builder

WORKDIR /build

RUN pip install --no-cache-dir --upgrade pip

COPY pyproject.toml ./
COPY app ./app

RUN pip install --no-cache-dir --prefix=/install .

# ---- Runtime stage ----
FROM python:3.12-slim AS runtime

WORKDIR /app

COPY --from=builder /install /usr/local
COPY app ./app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# M2M JWT validation config — set at deploy time (e.g. Cloud Run env vars / secrets).
ENV AUTH0_DOMAIN="" \
    AUTH0_AUDIENCE=""

RUN useradd --no-create-home --shell /usr/sbin/nologin appuser
USER appuser

EXPOSE 8000

# Cloud Run scales horizontally per instance — keep workers low (1-2), don't
# oversubscribe a single container.
CMD ["gunicorn", "app.main:app", "-k", "uvicorn.workers.UvicornWorker", "-w", "2", "-b", "0.0.0.0:8000"]
