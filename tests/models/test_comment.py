import pytest
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import Session

from personal_jira.models.base import Base
from personal_jira.models.comment import Comment, CommentType
from personal_jira.models.issue import Issue


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


class TestCommentType:
    def test_enum_values(self):
        assert CommentType.GENERAL.value == "general"
        assert CommentType.REVIEW.value == "review"
        assert CommentType.FEEDBACK.value == "feedback"

    def test_enum_members(self):
        assert set(CommentType.__members__.keys()) == {"GENERAL", "REVIEW", "FEEDBACK"}


class TestCommentSchema:
    def test_table_name(self):
        assert Comment.__tablename__ == "comments"

    def test_columns_exist(self, engine):
        inspector = inspect(engine)
        columns = {c["name"] for c in inspector.get_columns("comments")}
        expected = {"id", "issue_id", "author", "body_md", "comment_type", "created_at", "updated_at"}
        assert expected.issubset(columns)

    def test_primary_key(self, engine):
        inspector = inspect(engine)
        pk = inspector.get_pk_constraint("comments")
        assert "id" in pk["constrained_columns"]

    def test_foreign_keys(self, engine):
        inspector = inspect(engine)
        fks = inspector.get_foreign_keys("comments")
        fk_cols = {fk["constrained_columns"][0] for fk in fks}
        assert "issue_id" in fk_cols

    def test_issue_id_not_nullable(self, engine):
        inspector = inspect(engine)
        columns = {c["name"]: c for c in inspector.get_columns("comments")}
        assert columns["issue_id"]["nullable"] is False

    def test_author_not_nullable(self, engine):
        inspector = inspect(engine)
        columns = {c["name"]: c for c in inspector.get_columns("comments")}
        assert columns["author"]["nullable"] is False

    def test_body_md_not_nullable(self, engine):
        inspector = inspect(engine)
        columns = {c["name"]: c for c in inspector.get_columns("comments")}
        assert columns["body_md"]["nullable"] is False

    def test_index_on_issue_id(self, engine):
        inspector = inspect(engine)
        indexes = inspector.get_indexes("comments")
        index_names = {idx["name"] for idx in indexes}
        assert "ix_comments_issue_id" in index_names


class TestCommentCRUD:
    def test_create_comment(self, session):
        issue = Issue(title="Test Issue")
        session.add(issue)
        session.flush()

        comment = Comment(
            issue_id=issue.id,
            author="user1",
            body_md="This is a comment",
            comment_type=CommentType.GENERAL,
        )
        session.add(comment)
        session.flush()

        assert comment.id is not None
        assert comment.issue_id == issue.id
        assert comment.author == "user1"
        assert comment.body_md == "This is a comment"
        assert comment.comment_type == CommentType.GENERAL

    def test_comment_default_type(self, session):
        issue = Issue(title="Test Issue")
        session.add(issue)
        session.flush()

        comment = Comment(
            issue_id=issue.id,
            author="user1",
            body_md="Default type comment",
        )
        session.add(comment)
        session.flush()

        assert comment.comment_type == CommentType.GENERAL

    def test_comment_relationship(self, session):
        issue = Issue(title="Test Issue")
        session.add(issue)
        session.flush()

        comment = Comment(
            issue_id=issue.id,
            author="user1",
            body_md="Related comment",
        )
        session.add(comment)
        session.flush()

        assert comment.issue.id == issue.id
        assert comment in issue.comments
