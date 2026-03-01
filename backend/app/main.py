"""Application entrypoint."""

from fastapi import FastAPI

from app.api.fair import router as fair_router
from app.api.wallet import router as wallet_router
from app.api.crash import router as crash_router
from app.api.dice import router as dice_router
from app.api.mines import router as mines_router
from app.api.plinko import router as plinko_router
from app.api.payments import router as payments_router
from app.api.admin import router as admin_router
from app.api.ws import router as ws_router

app = FastAPI(title="Casino Platform API", version="0.2.0")
app.include_router(fair_router)
app.include_router(wallet_router)
app.include_router(crash_router)
app.include_router(dice_router)
app.include_router(mines_router)
app.include_router(plinko_router)
app.include_router(payments_router)
app.include_router(admin_router)
app.include_router(ws_router)


@app.get("/healthz")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}
