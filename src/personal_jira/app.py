from fastapi import FastAPI

from personal_jira.api.v1.endpoints.dependencies import router as dependencies_router


def create_app() -> FastAPI:
    app = FastAPI(title="Personal Jira", version="0.1.0")
    app.include_router(dependencies_router)
    return app
