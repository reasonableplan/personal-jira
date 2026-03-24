import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import IssueNotFoundException
from app.models import Issue
from app.services.issue_service import (
    create_issue,
    delete_issue,
    get_issue,
    list_issues,
    update_issue,
)


@pytest.mark.asyncio
async def test_create_issue(db_session: AsyncSession):
    issue = await create_issue(db_session, title="Test", description="Desc", priority="high")
    assert issue.id is not None
    assert issue.title == "Test"
    assert issue.description == "Desc"
    assert issue.priority == "high"
    assert issue.status == "todo"


@pytest.mark.asyncio
async def test_create_issue_defaults(db_session: AsyncSession):
    issue = await create_issue(db_session, title="Minimal")
    assert issue.priority == "medium"
    assert issue.status == "todo"


@pytest.mark.asyncio
async def test_get_issue(db_session: AsyncSession):
    issue = await create_issue(db_session, title="Find me")
    found = await get_issue(db_session, issue.id)
    assert found.id == issue.id
    assert found.title == "Find me"


@pytest.mark.asyncio
async def test_get_issue_not_found(db_session: AsyncSession):
    with pytest.raises(IssueNotFoundException):
        await get_issue(db_session, 99999)


@pytest.mark.asyncio
async def test_list_issues_empty(db_session: AsyncSession):
    items, total = await list_issues(db_session)
    assert items == []
    assert total == 0


@pytest.mark.asyncio
async def test_list_issues_pagination(db_session: AsyncSession):
    for i in range(5):
        await create_issue(db_session, title=f"Issue {i}")
    items, total = await list_issues(db_session, offset=1, limit=2)
    assert len(items) == 2
    assert total == 5


@pytest.mark.asyncio
async def test_list_issues_filter_status(db_session: AsyncSession):
    issue = await create_issue(db_session, title="Done issue")
    await update_issue(db_session, issue.id, status="done")
    await create_issue(db_session, title="Todo issue")

    items, total = await list_issues(db_session, status="done")
    assert total == 1
    assert items[0].title == "Done issue"


@pytest.mark.asyncio
async def test_list_issues_filter_priority(db_session: AsyncSession):
    await create_issue(db_session, title="High", priority="high")
    await create_issue(db_session, title="Low", priority="low")

    items, total = await list_issues(db_session, priority="high")
    assert total == 1
    assert items[0].title == "High"


@pytest.mark.asyncio
async def test_update_issue_partial(db_session: AsyncSession):
    issue = await create_issue(db_session, title="Original", description="Desc")
    updated = await update_issue(db_session, issue.id, title="Changed")
    assert updated.title == "Changed"
    assert updated.description == "Desc"


@pytest.mark.asyncio
async def test_update_issue_not_found(db_session: AsyncSession):
    with pytest.raises(IssueNotFoundException):
        await update_issue(db_session, 99999, title="Nope")


@pytest.mark.asyncio
async def test_delete_issue(db_session: AsyncSession):
    issue = await create_issue(db_session, title="Delete me")
    await delete_issue(db_session, issue.id)
    with pytest.raises(IssueNotFoundException):
        await get_issue(db_session, issue.id)


@pytest.mark.asyncio
async def test_delete_issue_not_found(db_session: AsyncSession):
    with pytest.raises(IssueNotFoundException):
        await delete_issue(db_session, 99999)
