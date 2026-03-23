import uuid
from datetime import datetime

from pydantic import BaseModel

ALLOWED_CONTENT_TYPES: frozenset[str] = frozenset({
    "image/png",
    "image/jpeg",
    "image/gif",
    "image/webp",
    "text/plain",
    "text/csv",
    "application/json",
    "application/pdf",
    "application/zip",
    "application/gzip",
    "application/octet-stream",
})

MAX_FILE_SIZE_BYTES: int = 10 * 1024 * 1024  # 10MB


class AttachmentResponse(BaseModel):
    id: uuid.UUID
    issue_id: uuid.UUID
    filename: str
    content_type: str
    file_size: int
    created_at: datetime

    model_config = {"from_attributes": True}
