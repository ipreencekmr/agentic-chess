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

RUN apt-get update && apt-get install -y --no-install-recommends nginx supervisor stockfish && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend ./backend
COPY app.py .
COPY deploy/nginx.hf.conf /etc/nginx/conf.d/default.conf
COPY deploy/supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY --from=frontend-build /app/frontend/dist /usr/share/nginx/html

EXPOSE 7860

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
