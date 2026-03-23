import pytest
from datetime import date, timedelta
from sqlalchemy import select

from personal_jira.models.sprint import Sprint, SprintStatus
from personal_jira.models.issue import Issue


class TestSprintModel:
    @pytest.mark.asyncio
    async def test_create_sprint(self, db_session):
        sprint = Sprint(
            name="Sprint 1",
            goal="Complete MVP features",
            start_date=date(2026, 3, 23),
            end_date=date(2026, 4, 6),
        )
        db_session.add(sprint)
        await db_session.commit()
        await db_session.refresh(sprint)

        assert sprint.id is not None
        assert sprint.name == "Sprint 1"
        assert sprint.goal == "Complete MVP features"
        assert sprint.status == SprintStatus.PLANNING
        assert sprint.start_date == date(2026, 3, 23)
        assert sprint.end_date == date(2026, 4, 6)
        assert sprint.created_at is not None
        assert sprint.updated_at is not None

    @pytest.mark.asyncio
    async def test_sprint_default_status(self, db_session):
        sprint = Sprint(
            name="Sprint 2",
            start_date=date(2026, 4, 6),
            end_date=date(2026, 4, 20),
        )
        db_session.add(sprint)
        await db_session.commit()
        await db_session.refresh(sprint)

        assert sprint.status == SprintStatus.PLANNING

    @pytest.mark.asyncio
    async def test_sprint_with_issues(self, db_session):
        sprint = Sprint(
            name="Sprint 3",
            start_date=date(2026, 4, 6),
            end_date=date(2026, 4, 20),
        )
        db_session.add(sprint)
        await db_session.commit()

        issue = Issue(
            title="Test Issue",
            sprint_id=sprint.id,
        )
        db_session.add(issue)
        await db_session.commit()

        await db_session.refresh(sprint)
        result = await db_session.execute(
            select(Issue).where(Issue.sprint_id == sprint.id)
        )
        issues = result.scalars().all()
        assert len(issues) == 1
        assert issues[0].title == "Test Issue"

    @pytest.mark.asyncio
    async def test_sprint_status_values(self):
        assert SprintStatus.PLANNING == "planning"
        assert SprintStatus.ACTIVE == "active"
        assert SprintStatus.COMPLETED == "completed"
        assert SprintStatus.CANCELLED == "cancelled"

    @pytest.mark.asyncio
    async def test_sprint_end_date_after_start(self, db_session):
        sprint = Sprint(
            name="Valid Sprint",
            start_date=date(2026, 4, 1),
            end_date=date(2026, 4, 15),
        )
        db_session.add(sprint)
        await db_session.commit()
        await db_session.refresh(sprint)
        assert sprint.end_date > sprint.start_date
