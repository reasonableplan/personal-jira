import pytest
from datetime import date
from uuid import uuid4

from pydantic import ValidationError

from personal_jira.schemas.sprint import (
    SprintCreate,
    SprintUpdate,
    SprintResponse,
    SprintListResponse,
    SprintIssueAdd,
)


class TestSprintCreateSchema:
    def test_valid_create(self):
        schema = SprintCreate(
            name="Sprint 1",
            goal="Ship MVP",
            start_date=date(2026, 3, 23),
            end_date=date(2026, 4, 6),
        )
        assert schema.name == "Sprint 1"
        assert schema.goal == "Ship MVP"

    def test_minimal_create(self):
        schema = SprintCreate(
            name="Sprint 1",
            start_date=date(2026, 3, 23),
            end_date=date(2026, 4, 6),
        )
        assert schema.goal is None

    def test_missing_name(self):
        with pytest.raises(ValidationError):
            SprintCreate(
                start_date=date(2026, 3, 23),
                end_date=date(2026, 4, 6),
            )

    def test_missing_dates(self):
        with pytest.raises(ValidationError):
            SprintCreate(name="Sprint 1")

    def test_end_before_start(self):
        with pytest.raises(ValidationError):
            SprintCreate(
                name="Sprint 1",
                start_date=date(2026, 4, 6),
                end_date=date(2026, 3, 23),
            )

    def test_empty_name(self):
        with pytest.raises(ValidationError):
            SprintCreate(
                name="",
                start_date=date(2026, 3, 23),
                end_date=date(2026, 4, 6),
            )


class TestSprintUpdateSchema:
    def test_partial_update_name(self):
        schema = SprintUpdate(name="Updated Sprint")
        data = schema.model_dump(exclude_unset=True)
        assert data == {"name": "Updated Sprint"}

    def test_partial_update_status(self):
        schema = SprintUpdate(status="active")
        data = schema.model_dump(exclude_unset=True)
        assert data == {"status": "active"}

    def test_empty_update(self):
        schema = SprintUpdate()
        data = schema.model_dump(exclude_unset=True)
        assert data == {}

    def test_invalid_status(self):
        with pytest.raises(ValidationError):
            SprintUpdate(status="invalid")


class TestSprintIssueAddSchema:
    def test_valid(self):
        issue_id = uuid4()
        schema = SprintIssueAdd(issue_id=issue_id)
        assert schema.issue_id == issue_id

    def test_missing_issue_id(self):
        with pytest.raises(ValidationError):
            SprintIssueAdd()
