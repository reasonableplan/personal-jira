import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator

from models.code_artifact import ArtifactType


class CodeArtifactCreate(BaseModel):
    artifact_type: ArtifactType
    identifier: str = Field(..., min_length=1)
    metadata_: dict[str, Any] | None = None


class CodeArtifactResponse(BaseModel):
    id: uuid.UUID
    issue_id: uuid.UUID
    artifact_type: ArtifactType
    identifier: str
    metadata_: dict[str, Any] | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
