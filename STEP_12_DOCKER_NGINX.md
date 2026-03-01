# STEP 12 — Docker + Nginx

Добавлены базовые production профили:

- `backend/Dockerfile`
- `docker-compose.yml`
- `deploy/nginx/nginx.conf`

Nginx проксирует REST и WebSocket на backend (`/v1/*`, `/healthz`).
