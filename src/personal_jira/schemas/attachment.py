import uuid

from pydantic import BaseModel


class AttachmentResponse(BaseModel):
    id: uuid.UUID
    issue_id: uuid.UUID
    filename: str
    content_type: str
    size_bytes: int
    created_at: str

    model_config = {"from_attributes": True}
