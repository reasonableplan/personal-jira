import pytest
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import Session

from personal_jira.models.base import Base
from personal_jira.models.issue import Issue
from personal_jira.models.issue_dependency import IssueDependency, DependencyType


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


class TestDependencyType:
    def test_enum_values(self):
        assert DependencyType.BLOCKED_BY.value == "blocked_by"
        assert DependencyType.BLOCKS.value == "blocks"

    def test_enum_members(self):
        assert set(DependencyType.__members__.keys()) == {"BLOCKED_BY", "BLOCKS"}


class TestIssueDependencySchema:
    def test_table_name(self):
        assert IssueDependency.__tablename__ == "issue_dependencies"

    def test_columns_exist(self, engine):
        inspector = inspect(engine)
        columns = {c["name"] for c in inspector.get_columns("issue_dependencies")}
        expected = {"id", "from_issue_id", "to_issue_id", "dependency_type", "created_at"}
        assert expected.issubset(columns)

    def test_foreign_keys(self, engine):
        inspector = inspect(engine)
        fks = inspector.get_foreign_keys("issue_dependencies")
        fk_cols = {fk["constrained_columns"][0] for fk in fks}
        assert "from_issue_id" in fk_cols
        assert "to_issue_id" in fk_cols

    def test_unique_constraint(self, engine):
        inspector = inspect(engine)
        uniques = inspector.get_unique_constraints("issue_dependencies")
        found = False
        for u in uniques:
            if set(u["column_names"]) == {"from_issue_id", "to_issue_id"}:
                found = True
        assert found

    def test_indexes(self, engine):
        inspector = inspect(engine)
        indexes = inspector.get_indexes("issue_dependencies")
        index_names = {idx["name"] for idx in indexes}
        assert "ix_issue_dep_from" in index_names
        assert "ix_issue_dep_to" in index_names


class TestIssueDependencyCRUD:
    def test_create_dependency(self, session):
        issue1 = Issue(title="Issue 1")
        issue2 = Issue(title="Issue 2")
        session.add_all([issue1, issue2])
        session.flush()

        dep = IssueDependency(
            from_issue_id=issue1.id,
            to_issue_id=issue2.id,
            dependency_type=DependencyType.BLOCKED_BY,
        )
        session.add(dep)
        session.flush()

        assert dep.id is not None
        assert dep.from_issue_id == issue1.id
        assert dep.to_issue_id == issue2.id
        assert dep.dependency_type == DependencyType.BLOCKED_BY

    def test_unique_pair_constraint(self, session):
        issue1 = Issue(title="Issue 1")
        issue2 = Issue(title="Issue 2")
        session.add_all([issue1, issue2])
        session.flush()

        dep1 = IssueDependency(
            from_issue_id=issue1.id,
            to_issue_id=issue2.id,
            dependency_type=DependencyType.BLOCKED_BY,
        )
        session.add(dep1)
        session.flush()

        dep2 = IssueDependency(
            from_issue_id=issue1.id,
            to_issue_id=issue2.id,
            dependency_type=DependencyType.BLOCKS,
        )
        session.add(dep2)
        with pytest.raises(Exception):
            session.flush()

    def test_relationship_from_issue(self, session):
        issue1 = Issue(title="Issue 1")
        issue2 = Issue(title="Issue 2")
        session.add_all([issue1, issue2])
        session.flush()

        dep = IssueDependency(
            from_issue_id=issue1.id,
            to_issue_id=issue2.id,
            dependency_type=DependencyType.BLOCKED_BY,
        )
        session.add(dep)
        session.flush()

        assert dep.from_issue.id == issue1.id
        assert dep.to_issue.id == issue2.id
        assert dep in issue1.dependencies_from
        assert dep in issue2.dependencies_to
