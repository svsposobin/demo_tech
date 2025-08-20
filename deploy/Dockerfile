FROM python:3.12-slim

WORKDIR /app

# Устанавливаем системные зависимости для psycopg
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements-prod.txt .

RUN --mount=type=cache,target=/root/.cache \
    pip install --no-cache-dir -r requirements-prod.txt && \
    rm -rf /root/.cache/pip && \
    find /usr/local/lib -type d -name '__pycache__' -exec rm -rf {} +

COPY . .

COPY deploy/start.sh ./start.sh
RUN chmod +x ./start.sh

CMD ["./start.sh"]
