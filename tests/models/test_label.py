import pytest
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import Session

from personal_jira.models.base import Base
from personal_jira.models.label import Label


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


class TestLabelSchema:
    def test_table_name(self):
        assert Label.__tablename__ == "labels"

    def test_columns_exist(self, engine):
        inspector = inspect(engine)
        columns = {c["name"] for c in inspector.get_columns("labels")}
        expected = {"id", "name", "color", "created_at"}
        assert expected.issubset(columns)

    def test_primary_key(self, engine):
        inspector = inspect(engine)
        pk = inspector.get_pk_constraint("labels")
        assert "id" in pk["constrained_columns"]

    def test_name_not_nullable(self, engine):
        inspector = inspect(engine)
        columns = {c["name"]: c for c in inspector.get_columns("labels")}
        assert columns["name"]["nullable"] is False

    def test_name_unique(self, engine):
        inspector = inspect(engine)
        uniques = inspector.get_unique_constraints("labels")
        unique_cols = set()
        for u in uniques:
            for col in u["column_names"]:
                unique_cols.add(col)
        assert "name" in unique_cols

    def test_color_not_nullable(self, engine):
        inspector = inspect(engine)
        columns = {c["name"]: c for c in inspector.get_columns("labels")}
        assert columns["color"]["nullable"] is False


class TestLabelCRUD:
    def test_create_label(self, session):
        label = Label(name="bug", color="#ff0000")
        session.add(label)
        session.flush()

        assert label.id is not None
        assert label.name == "bug"
        assert label.color == "#ff0000"

    def test_unique_name_constraint(self, session):
        label1 = Label(name="bug", color="#ff0000")
        session.add(label1)
        session.flush()

        label2 = Label(name="bug", color="#00ff00")
        session.add(label2)
        with pytest.raises(Exception):
            session.flush()
