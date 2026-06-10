from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.api.models.ml_model import load_model
from src.api.routes import health, model_info, predict


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        load_model()
    except Exception as e:
        print(f"[STARTUP ERROR] load_model failed: {e}", flush=True)
    yield


app = FastAPI(title="ModelShip", lifespan=lifespan)

app.include_router(health.router)
app.include_router(predict.router)
app.include_router(model_info.router)
