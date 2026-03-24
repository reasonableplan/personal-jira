from fastapi import FastAPI

from app.core.config import get_settings

_settings = get_settings()

app = FastAPI(title=_settings.APP_NAME, debug=_settings.DEBUG)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
