from app.core.config import get_settings
from app.routers.health import router as health_router
from fastapi import FastAPI

_settings = get_settings()

app = FastAPI(title=_settings.APP_NAME, debug=_settings.DEBUG)

app.include_router(health_router)
