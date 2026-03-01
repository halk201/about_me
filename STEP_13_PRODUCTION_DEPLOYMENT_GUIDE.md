# STEP 13 — Production Deployment Guide

## Минимальный pipeline
1. Build images (backend/frontend/nginx)
2. Run migrations (Alembic)
3. Start services behind load balancer
4. Warm-up + health checks
5. Enable traffic gradually (canary)

## SLO/операции
- API p95 < 200ms
- WS reconnect success > 99.9%
- Settlement lag < 2s

## Безопасность
- JWT short-lived + refresh rotation
- KMS/Secrets manager for seeds/keys
- Immutable audit log + centralized monitoring
