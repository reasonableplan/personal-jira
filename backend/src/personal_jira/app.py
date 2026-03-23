from fastapi import FastAPI

from personal_jira.api.health import router as health_router
from personal_jira.config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG)
    app.include_router(health_router)
    return app
