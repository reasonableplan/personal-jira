from app.config import settings
from app.exceptions import register_exception_handlers
from app.routers.labels import router as labels_router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Personal Jira", debug=settings.debug)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

app.include_router(labels_router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
