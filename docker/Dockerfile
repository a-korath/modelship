# Stage 1: install dependencies
FROM python:3.11-slim AS builder

WORKDIR /build

COPY pyproject.toml .
RUN pip install --upgrade pip && \
    pip install --prefix=/install ".[ml]"

# Stage 2: lean runtime image
FROM python:3.11-slim AS runtime

WORKDIR /app

ENV PYTHONUNBUFFERED=1

# copy installed packages from builder
COPY --from=builder /install /usr/local

# copy application code
COPY src/ ./src/

CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
