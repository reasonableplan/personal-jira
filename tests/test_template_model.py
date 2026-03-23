import uuid

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from personal_jira.models.base import Base
from personal_jira.models.template import IssueTemplate


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


class TestIssueTemplateModel:
    def test_create_template(self, db: Session) -> None:
        template = IssueTemplate(
            name="Bug Report",
            title_pattern="[BUG] {summary}",
            description_template="## Steps to reproduce\n\n## Expected\n\n## Actual",
            default_priority="high",
            default_issue_type="bug",
            default_labels=["bug", "triage"],
        )
        db.add(template)
        db.commit()
        db.refresh(template)

        assert template.id is not None
        assert isinstance(template.id, uuid.UUID)
        assert template.name == "Bug Report"
        assert template.default_labels == ["bug", "triage"]

    def test_template_without_optional_fields(self, db: Session) -> None:
        template = IssueTemplate(
            name="Simple Task",
            title_pattern="{summary}",
        )
        db.add(template)
        db.commit()
        db.refresh(template)

        assert template.description_template is None
        assert template.default_priority is None
        assert template.default_issue_type is None
        assert template.default_labels is None

    def test_template_uuid_primary_key(self, db: Session) -> None:
        template = IssueTemplate(
            name="Feature Request",
            title_pattern="[FEAT] {summary}",
        )
        db.add(template)
        db.commit()
        db.refresh(template)

        assert isinstance(template.id, uuid.UUID)
