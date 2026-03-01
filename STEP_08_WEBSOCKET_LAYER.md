# STEP 8 — WebSocket Layer

Добавлен WebSocket слой с replay buffer по sequence id.

- WS endpoint: `GET /v1/ws/replay/{seq}`, `WS /v1/ws`
- Сервис: `backend/app/services/ws_service.py`
- Event contracts расширены в `backend/app/ws/events.py`.
