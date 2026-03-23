from datetime import date
from uuid import uuid4

import pytest
from pydantic import ValidationError

from personal_jira.schemas.sprint import (
    SprintCreate,
    SprintResponse,
    SprintUpdate,
)


class TestSprintCreateSchema:
    def test_valid_create(self) -> None:
        data = SprintCreate(
            name="Sprint 1",
            goal="Finish MVP",
            start_date=date(2026, 3, 1),
            end_date=date(2026, 3, 14),
        )
        assert data.name == "Sprint 1"
        assert data.goal == "Finish MVP"

    def test_create_without_goal(self) -> None:
        data = SprintCreate(
            name="Sprint 1",
            start_date=date(2026, 3, 1),
            end_date=date(2026, 3, 14),
        )
        assert data.goal is None

    def test_create_missing_name(self) -> None:
        with pytest.raises(ValidationError):
            SprintCreate(
                start_date=date(2026, 3, 1),
                end_date=date(2026, 3, 14),
            )

    def test_create_missing_dates(self) -> None:
        with pytest.raises(ValidationError):
            SprintCreate(name="Sprint 1")

    def test_create_end_before_start(self) -> None:
        with pytest.raises(ValidationError):
            SprintCreate(
                name="Sprint 1",
                start_date=date(2026, 3, 14),
                end_date=date(2026, 3, 1),
            )

    def test_create_empty_name(self) -> None:
        with pytest.raises(ValidationError):
            SprintCreate(
                name="",
                start_date=date(2026, 3, 1),
                end_date=date(2026, 3, 14),
            )


class TestSprintUpdateSchema:
    def test_partial_update_name(self) -> None:
        data = SprintUpdate(name="Updated Sprint")
        dumped = data.model_dump(exclude_unset=True)
        assert dumped == {"name": "Updated Sprint"}

    def test_partial_update_status(self) -> None:
        data = SprintUpdate(status="active")
        dumped = data.model_dump(exclude_unset=True)
        assert dumped == {"status": "active"}

    def test_empty_update(self) -> None:
        data = SprintUpdate()
        dumped = data.model_dump(exclude_unset=True)
        assert dumped == {}

    def test_invalid_status(self) -> None:
        with pytest.raises(ValidationError):
            SprintUpdate(status="invalid_status")


class TestSprintResponseSchema:
    def test_response_from_attributes(self) -> None:
        sprint_id = uuid4()
        data = SprintResponse(
            id=sprint_id,
            name="Sprint 1",
            goal="Goal",
            status="planning",
            start_date=date(2026, 3, 1),
            end_date=date(2026, 3, 14),
        )
        assert data.id == sprint_id
        assert data.name == "Sprint 1"
