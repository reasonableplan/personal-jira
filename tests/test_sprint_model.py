import uuid
from datetime import date, timedelta

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from personal_jira.models.base import Base
from personal_jira.models.sprint import Sprint, SprintStatus


@pytest.fixture
def engine():
    eng = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(eng)
    yield eng
    Base.metadata.drop_all(eng)


@pytest.fixture
def db(engine) -> Session:
    session_factory = sessionmaker(bind=engine)
    session = session_factory()
    yield session
    session.close()


class TestSprintModel:
    def test_create_sprint(self, db: Session) -> None:
        sprint = Sprint(
            name="Sprint 1",
            goal="Complete auth module",
            start_date=date(2026, 3, 1),
            end_date=date(2026, 3, 14),
        )
        db.add(sprint)
        db.commit()
        db.refresh(sprint)

        assert sprint.id is not None
        assert sprint.name == "Sprint 1"
        assert sprint.goal == "Complete auth module"
        assert sprint.status == SprintStatus.PLANNING
        assert sprint.start_date == date(2026, 3, 1)
        assert sprint.end_date == date(2026, 3, 14)
        assert sprint.created_at is not None

    def test_sprint_status_enum(self) -> None:
        assert SprintStatus.PLANNING == "planning"
        assert SprintStatus.ACTIVE == "active"
        assert SprintStatus.COMPLETED == "completed"
        assert SprintStatus.CANCELLED == "cancelled"

    def test_sprint_default_status(self, db: Session) -> None:
        sprint = Sprint(
            name="Sprint 2",
            start_date=date(2026, 4, 1),
            end_date=date(2026, 4, 14),
        )
        db.add(sprint)
        db.commit()
        db.refresh(sprint)

        assert sprint.status == SprintStatus.PLANNING

    def test_sprint_uuid_primary_key(self, db: Session) -> None:
        sprint = Sprint(
            name="Sprint 3",
            start_date=date(2026, 5, 1),
            end_date=date(2026, 5, 14),
        )
        db.add(sprint)
        db.commit()
        db.refresh(sprint)

        assert isinstance(sprint.id, uuid.UUID)

    def test_sprint_without_goal(self, db: Session) -> None:
        sprint = Sprint(
            name="Sprint 4",
            start_date=date(2026, 6, 1),
            end_date=date(2026, 6, 14),
        )
        db.add(sprint)
        db.commit()
        db.refresh(sprint)

        assert sprint.goal is None
