#можно сразу отправлять http запросы от клиента

from fastapi import FastAPI
from api.routes import router

app = FastAPI(
    title="Astra_prog API",
    version="0.1.0",
    description="API for parsing logs and saving datasets (DB/CSV).",
)

app.include_router(router, prefix="/api/v1")


@app.get("/health")
def health():
    return {"status": "ok"}