from fastapi import FastAPI

from personal_jira.routers.issues import router as issues_router


def create_app() -> FastAPI:
    app = FastAPI(title="Personal Jira", version="0.1.0")
    app.include_router(issues_router)
    return app


app = create_app()
