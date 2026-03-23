import pytest
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import Session

from personal_jira.models.base import Base
from personal_jira.models.issue import Issue
from personal_jira.models.label import Label
from personal_jira.models.issue_label import IssueLabel


@pytest.fixture
def engine():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)


@pytest.fixture
def session(engine):
    with Session(engine) as session:
        yield session


class TestIssueLabelSchema:
    def test_table_name(self):
        assert IssueLabel.__tablename__ == "issue_labels"

    def test_columns_exist(self, engine):
        inspector = inspect(engine)
        columns = {c["name"] for c in inspector.get_columns("issue_labels")}
        expected = {"id", "issue_id", "label_id", "created_at"}
        assert expected.issubset(columns)

    def test_foreign_keys(self, engine):
        inspector = inspect(engine)
        fks = inspector.get_foreign_keys("issue_labels")
        fk_cols = {fk["constrained_columns"][0] for fk in fks}
        assert "issue_id" in fk_cols
        assert "label_id" in fk_cols

    def test_unique_constraint(self, engine):
        inspector = inspect(engine)
        uniques = inspector.get_unique_constraints("issue_labels")
        found = False
        for u in uniques:
            if set(u["column_names"]) == {"issue_id", "label_id"}:
                found = True
        assert found

    def test_indexes(self, engine):
        inspector = inspect(engine)
        indexes = inspector.get_indexes("issue_labels")
        index_names = {idx["name"] for idx in indexes}
        assert "ix_issue_labels_issue_id" in index_names
        assert "ix_issue_labels_label_id" in index_names


class TestIssueLabelCRUD:
    def test_create_issue_label(self, session):
        issue = Issue(title="Test Issue")
        label = Label(name="bug", color="#ff0000")
        session.add_all([issue, label])
        session.flush()

        issue_label = IssueLabel(issue_id=issue.id, label_id=label.id)
        session.add(issue_label)
        session.flush()

        assert issue_label.id is not None
        assert issue_label.issue_id == issue.id
        assert issue_label.label_id == label.id

    def test_unique_issue_label_pair(self, session):
        issue = Issue(title="Test Issue")
        label = Label(name="bug", color="#ff0000")
        session.add_all([issue, label])
        session.flush()

        il1 = IssueLabel(issue_id=issue.id, label_id=label.id)
        session.add(il1)
        session.flush()

        il2 = IssueLabel(issue_id=issue.id, label_id=label.id)
        session.add(il2)
        with pytest.raises(Exception):
            session.flush()

    def test_m2m_relationship(self, session):
        issue = Issue(title="Test Issue")
        label1 = Label(name="bug", color="#ff0000")
        label2 = Label(name="feature", color="#00ff00")
        session.add_all([issue, label1, label2])
        session.flush()

        session.add_all([
            IssueLabel(issue_id=issue.id, label_id=label1.id),
            IssueLabel(issue_id=issue.id, label_id=label2.id),
        ])
        session.flush()

        assert len(issue.issue_labels) == 2
        assert len(label1.issue_labels) == 1
