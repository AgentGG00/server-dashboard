FROM node:20-slim AS frontend-build
WORKDIR /app/frontend
COPY src/frontend/package*.json ./
RUN npm ci
COPY src/frontend ./
RUN NODE_ENV=production npm run build

FROM python:3.12-slim
WORKDIR /app

RUN apt-get update && apt-get install -y supervisor nodejs && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/backend ./src/backend
COPY --from=frontend-build /app/frontend/build ./frontend/build
COPY --from=frontend-build /app/frontend/node_modules ./frontend/node_modules

COPY config/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

EXPOSE 8000 3000
CMD ["supervisord", "-n", "-c", "/etc/supervisor/conf.d/supervisord.conf"]