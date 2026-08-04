FROM python:3.11-slim

WORKDIR /app/backend

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PIP_DEFAULT_TIMEOUT=120
ENV PIP_RETRIES=10
ENV ANONYMIZED_TELEMETRY=False

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential curl gosu \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN python -m pip install --upgrade pip \
    && python -m pip install --no-cache-dir --default-timeout=120 --retries=10 --prefer-binary -r requirements.txt

COPY . .

# Create a non-root user and group, create directories, and set permissions
RUN groupadd -g 10001 appgroup && \
    useradd -u 10001 -g appgroup -d /app/backend -s /bin/bash appuser && \
    mkdir -p /app/backend/uploads /app/backend/chroma_db && \
    chown -R appuser:appgroup /app/backend && \
    chmod +x /app/backend/docker-entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/app/backend/docker-entrypoint.sh"]

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
