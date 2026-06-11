import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

logger = logging.getLogger(__name__)

from src.api.models.ml_model import load_model
from src.api.routes import api_keys, health, model_info, predict


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        load_model()
    except Exception:
        logger.exception("[STARTUP ERROR] load_model failed")
    yield


app = FastAPI(title="ModelShip", lifespan=lifespan)

app.include_router(health.router)
app.include_router(predict.router)
app.include_router(model_info.router)
app.include_router(api_keys.router)
