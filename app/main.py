from fastapi import FastAPI

from app.api.agents import router as agents_router
from app.api.claim import router as claim_router


def create_app() -> FastAPI:
    app = FastAPI(title="Issue Tracker API", version="1.0.0")
    app.include_router(agents_router)
    app.include_router(claim_router)
    return app


app = create_app()
