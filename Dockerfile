FROM node:20-alpine AS frontend-build

WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend .
RUN npm run build

FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies including wget for Jaeger
RUN apt-get update && apt-get install -y --no-install-recommends \
    nginx \
    supervisor \
    stockfish \
    wget \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Download and install Jaeger all-in-one binary
RUN wget https://github.com/jaegertracing/jaeger/releases/download/v1.57.0/jaeger-1.57.0-linux-amd64.tar.gz \
    && tar -xzf jaeger-1.57.0-linux-amd64.tar.gz \
    && mv jaeger-1.57.0-linux-amd64/jaeger-all-in-one /usr/local/bin/ \
    && rm -rf jaeger-1.57.0-linux-amd64* \
    && chmod +x /usr/local/bin/jaeger-all-in-one

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend ./backend
COPY app.py .
COPY deploy/nginx.hf.conf /etc/nginx/conf.d/default.conf
COPY deploy/supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY --from=frontend-build /app/frontend/dist /usr/share/nginx/html

# Set environment variables for telemetry (Jaeger runs on localhost in same container)
ENV OTEL_ENABLED=true \
    OTEL_SERVICE_NAME=agentic-chess \
    OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317

EXPOSE 7860

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
