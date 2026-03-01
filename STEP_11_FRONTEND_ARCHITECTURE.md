# STEP 11 — Frontend Architecture (React + TypeScript + Zustand)

Подготовлен фронтенд-скелет модульной архитектуры для интеграции с backend/WS:

- `frontend/src/app/router.tsx` — роутинг
- `frontend/src/stores/*` — Zustand stores (`auth`, `wallet`, `games`, `ws`)
- `frontend/src/ws/client.ts` — reconnect/replay-ready WS client
- `frontend/src/pages/*` — игровые страницы (Crash/Dice/Mines/Plinko), History, Leaderboard

Примечание: прямой HTML/CSS-parity с reference-сайтом требует сетевого доступа/снимка страницы.
