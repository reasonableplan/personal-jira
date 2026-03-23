import uuid
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from personal_jira.models.comment import Comment, CommentType
from personal_jira.schemas.comment import CommentCreate, CommentUpdate, CommentResponse


@pytest.fixture
def issue_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def comment_id() -> uuid.UUID:
    return uuid.uuid4()


def _make_comment(
    comment_id: uuid.UUID,
    issue_id: uuid.UUID,
    author: str = "user-1",
    content: str = "# Heading\nSome **markdown** content",
    comment_type: CommentType = CommentType.GENERAL,
) -> Comment:
    now = datetime.now(timezone.utc)
    comment = Comment(
        id=comment_id,
        issue_id=issue_id,
        author=author,
        content=content,
        comment_type=comment_type.value,
        created_at=now,
        updated_at=now,
    )
    return comment


class TestCommentCreateSchema:
    def test_valid_create(self) -> None:
        data = CommentCreate(
            author="user-1",
            content="# Title\nBody",
            comment_type="general",
        )
        assert data.author == "user-1"
        assert data.content == "# Title\nBody"
        assert data.comment_type == "general"

    def test_default_comment_type(self) -> None:
        data = CommentCreate(author="user-1", content="text")
        assert data.comment_type == "general"

    def test_missing_author(self) -> None:
        with pytest.raises(Exception):
            CommentCreate(content="text")

    def test_missing_content(self) -> None:
        with pytest.raises(Exception):
            CommentCreate(author="user-1")

    def test_empty_content_rejected(self) -> None:
        with pytest.raises(Exception):
            CommentCreate(author="user-1", content="")

    def test_empty_author_rejected(self) -> None:
        with pytest.raises(Exception):
            CommentCreate(author="", content="text")

    def test_invalid_comment_type(self) -> None:
        with pytest.raises(Exception):
            CommentCreate(author="user-1", content="text", comment_type="invalid")

    def test_all_comment_types(self) -> None:
        for ct in ["general", "review", "feedback"]:
            data = CommentCreate(author="user-1", content="text", comment_type=ct)
            assert data.comment_type == ct


class TestCommentUpdateSchema:
    def test_partial_content(self) -> None:
        data = CommentUpdate(content="updated")
        dumped = data.model_dump(exclude_unset=True)
        assert dumped == {"content": "updated"}

    def test_partial_comment_type(self) -> None:
        data = CommentUpdate(comment_type="review")
        dumped = data.model_dump(exclude_unset=True)
        assert dumped == {"comment_type": "review"}

    def test_empty_body(self) -> None:
        data = CommentUpdate()
        dumped = data.model_dump(exclude_unset=True)
        assert dumped == {}

    def test_empty_content_rejected(self) -> None:
        with pytest.raises(Exception):
            CommentUpdate(content="")

    def test_invalid_comment_type_rejected(self) -> None:
        with pytest.raises(Exception):
            CommentUpdate(comment_type="invalid")


class TestCommentResponseSchema:
    def test_from_model(self, issue_id: uuid.UUID, comment_id: uuid.UUID) -> None:
        comment = _make_comment(comment_id, issue_id)
        resp = CommentResponse.model_validate(comment, from_attributes=True)
        assert resp.id == comment_id
        assert resp.issue_id == issue_id
        assert resp.author == "user-1"
        assert resp.content == "# Heading\nSome **markdown** content"
        assert resp.comment_type == "general"
        assert resp.created_at is not None
        assert resp.updated_at is not None


class TestCreateCommentAPI:
    @pytest.fixture
    def mock_db(self):
        db = MagicMock()
        db.commit = MagicMock()
        db.refresh = MagicMock()
        db.add = MagicMock()
        return db

    def test_create_comment_success(
        self, mock_db: MagicMock, issue_id: uuid.UUID, comment_id: uuid.UUID
    ) -> None:
        from personal_jira.routers.comment import create_comment

        issue = MagicMock()
        issue.id = issue_id
        issue.deleted_at = None
        mock_db.get.return_value = issue

        def _refresh(obj: Comment) -> None:
            obj.id = comment_id
            obj.created_at = datetime.now(timezone.utc)
            obj.updated_at = datetime.now(timezone.utc)

        mock_db.refresh.side_effect = _refresh

        body = CommentCreate(author="user-1", content="# Hello", comment_type="general")
        result = create_comment(issue_id=issue_id, body=body, db=mock_db)

        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        assert result.author == "user-1"
        assert result.content == "# Hello"

    def test_create_comment_issue_not_found(self, mock_db: MagicMock) -> None:
        from fastapi import HTTPException
        from personal_jira.routers.comment import create_comment

        mock_db.get.return_value = None
        body = CommentCreate(author="user-1", content="text")

        with pytest.raises(HTTPException) as exc_info:
            create_comment(issue_id=uuid.uuid4(), body=body, db=mock_db)
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND

    def test_create_comment_deleted_issue(self, mock_db: MagicMock) -> None:
        from fastapi import HTTPException
        from personal_jira.routers.comment import create_comment

        issue = MagicMock()
        issue.deleted_at = datetime.now(timezone.utc)
        mock_db.get.return_value = issue
        body = CommentCreate(author="user-1", content="text")

        with pytest.raises(HTTPException) as exc_info:
            create_comment(issue_id=uuid.uuid4(), body=body, db=mock_db)
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND

    def test_create_review_comment(
        self, mock_db: MagicMock, issue_id: uuid.UUID, comment_id: uuid.UUID
    ) -> None:
        from personal_jira.routers.comment import create_comment

        issue = MagicMock()
        issue.id = issue_id
        issue.deleted_at = None
        mock_db.get.return_value = issue

        def _refresh(obj: Comment) -> None:
            obj.id = comment_id
            obj.created_at = datetime.now(timezone.utc)
            obj.updated_at = datetime.now(timezone.utc)

        mock_db.refresh.side_effect = _refresh

        body = CommentCreate(author="user-1", content="LGTM", comment_type="review")
        result = create_comment(issue_id=issue_id, body=body, db=mock_db)
        assert result.comment_type == "review"


class TestListCommentsAPI:
    @pytest.fixture
    def mock_db(self):
        return MagicMock()

    def test_list_empty(self, mock_db: MagicMock, issue_id: uuid.UUID) -> None:
        from personal_jira.routers.comment import list_comments

        issue = MagicMock()
        issue.deleted_at = None
        mock_db.get.return_value = issue

        query_mock = MagicMock()
        query_mock.filter.return_value = query_mock
        query_mock.order_by.return_value = query_mock
        query_mock.offset.return_value = query_mock
        query_mock.limit.return_value = query_mock
        query_mock.all.return_value = []
        mock_db.query.return_value = query_mock

        result = list_comments(issue_id=issue_id, db=mock_db)
        assert result == []

    def test_list_with_comments(
        self, mock_db: MagicMock, issue_id: uuid.UUID
    ) -> None:
        from personal_jira.routers.comment import list_comments

        issue = MagicMock()
        issue.deleted_at = None
        mock_db.get.return_value = issue

        comments = [
            _make_comment(uuid.uuid4(), issue_id, author="a"),
            _make_comment(uuid.uuid4(), issue_id, author="b"),
        ]
        query_mock = MagicMock()
        query_mock.filter.return_value = query_mock
        query_mock.order_by.return_value = query_mock
        query_mock.offset.return_value = query_mock
        query_mock.limit.return_value = query_mock
        query_mock.all.return_value = comments
        mock_db.query.return_value = query_mock

        result = list_comments(issue_id=issue_id, db=mock_db)
        assert len(result) == 2

    def test_list_issue_not_found(self, mock_db: MagicMock) -> None:
        from fastapi import HTTPException
        from personal_jira.routers.comment import list_comments

        mock_db.get.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            list_comments(issue_id=uuid.uuid4(), db=mock_db)
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND

    def test_list_with_pagination(
        self, mock_db: MagicMock, issue_id: uuid.UUID
    ) -> None:
        from personal_jira.routers.comment import list_comments

        issue = MagicMock()
        issue.deleted_at = None
        mock_db.get.return_value = issue

        query_mock = MagicMock()
        query_mock.filter.return_value = query_mock
        query_mock.order_by.return_value = query_mock
        query_mock.offset.return_value = query_mock
        query_mock.limit.return_value = query_mock
        query_mock.all.return_value = []
        mock_db.query.return_value = query_mock

        list_comments(issue_id=issue_id, db=mock_db, offset=10, limit=5)
        query_mock.offset.assert_called_once_with(10)
        query_mock.limit.assert_called_once_with(5)


class TestUpdateCommentAPI:
    @pytest.fixture
    def mock_db(self):
        db = MagicMock()
        db.commit = MagicMock()
        db.refresh = MagicMock()
        return db

    def test_update_content(
        self, mock_db: MagicMock, issue_id: uuid.UUID, comment_id: uuid.UUID
    ) -> None:
        from personal_jira.routers.comment import update_comment

        issue = MagicMock()
        issue.deleted_at = None
        mock_db.get.return_value = issue

        comment = _make_comment(comment_id, issue_id)
        query_mock = MagicMock()
        query_mock.filter.return_value = query_mock
        query_mock.first.return_value = comment
        mock_db.query.return_value = query_mock

        body = CommentUpdate(content="updated content")
        result = update_comment(
            issue_id=issue_id, comment_id=comment_id, body=body, db=mock_db
        )
        assert result.content == "updated content"
        mock_db.commit.assert_called_once()

    def test_update_comment_type(
        self, mock_db: MagicMock, issue_id: uuid.UUID, comment_id: uuid.UUID
    ) -> None:
        from personal_jira.routers.comment import update_comment

        issue = MagicMock()
        issue.deleted_at = None
        mock_db.get.return_value = issue

        comment = _make_comment(comment_id, issue_id)
        query_mock = MagicMock()
        query_mock.filter.return_value = query_mock
        query_mock.first.return_value = comment
        mock_db.query.return_value = query_mock

        body = CommentUpdate(comment_type="feedback")
        result = update_comment(
            issue_id=issue_id, comment_id=comment_id, body=body, db=mock_db
        )
        assert result.comment_type == "feedback"

    def test_update_empty_body(
        self, mock_db: MagicMock, issue_id: uuid.UUID, comment_id: uuid.UUID
    ) -> None:
        from personal_jira.routers.comment import update_comment

        issue = MagicMock()
        issue.deleted_at = None
        mock_db.get.return_value = issue

        comment = _make_comment(comment_id, issue_id)
        query_mock = MagicMock()
        query_mock.filter.return_value = query_mock
        query_mock.first.return_value = comment
        mock_db.query.return_value = query_mock

        body = CommentUpdate()
        result = update_comment(
            issue_id=issue_id, comment_id=comment_id, body=body, db=mock_db
        )
        assert result.content == comment.content
        mock_db.commit.assert_called_once()

    def test_update_comment_not_found(
        self, mock_db: MagicMock, issue_id: uuid.UUID
    ) -> None:
        from fastapi import HTTPException
        from personal_jira.routers.comment import update_comment

        issue = MagicMock()
        issue.deleted_at = None
        mock_db.get.return_value = issue

        query_mock = MagicMock()
        query_mock.filter.return_value = query_mock
        query_mock.first.return_value = None
        mock_db.query.return_value = query_mock

        body = CommentUpdate(content="x")
        with pytest.raises(HTTPException) as exc_info:
            update_comment(
                issue_id=issue_id, comment_id=uuid.uuid4(), body=body, db=mock_db
            )
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND

    def test_update_issue_not_found(
        self, mock_db: MagicMock, comment_id: uuid.UUID
    ) -> None:
        from fastapi import HTTPException
        from personal_jira.routers.comment import update_comment

        mock_db.get.return_value = None
        body = CommentUpdate(content="x")

        with pytest.raises(HTTPException) as exc_info:
            update_comment(
                issue_id=uuid.uuid4(), comment_id=comment_id, body=body, db=mock_db
            )
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND


class TestDeleteCommentAPI:
    @pytest.fixture
    def mock_db(self):
        db = MagicMock()
        db.commit = MagicMock()
        db.delete = MagicMock()
        return db

    def test_delete_success(
        self, mock_db: MagicMock, issue_id: uuid.UUID, comment_id: uuid.UUID
    ) -> None:
        from personal_jira.routers.comment import delete_comment

        issue = MagicMock()
        issue.deleted_at = None
        mock_db.get.return_value = issue

        comment = _make_comment(comment_id, issue_id)
        query_mock = MagicMock()
        query_mock.filter.return_value = query_mock
        query_mock.first.return_value = comment
        mock_db.query.return_value = query_mock

        result = delete_comment(
            issue_id=issue_id, comment_id=comment_id, db=mock_db
        )
        mock_db.delete.assert_called_once_with(comment)
        mock_db.commit.assert_called_once()
        assert result is None

    def test_delete_comment_not_found(
        self, mock_db: MagicMock, issue_id: uuid.UUID
    ) -> None:
        from fastapi import HTTPException
        from personal_jira.routers.comment import delete_comment

        issue = MagicMock()
        issue.deleted_at = None
        mock_db.get.return_value = issue

        query_mock = MagicMock()
        query_mock.filter.return_value = query_mock
        query_mock.first.return_value = None
        mock_db.query.return_value = query_mock

        with pytest.raises(HTTPException) as exc_info:
            delete_comment(
                issue_id=issue_id, comment_id=uuid.uuid4(), db=mock_db
            )
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_issue_not_found(
        self, mock_db: MagicMock, comment_id: uuid.UUID
    ) -> None:
        from fastapi import HTTPException
        from personal_jira.routers.comment import delete_comment

        mock_db.get.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            delete_comment(
                issue_id=uuid.uuid4(), comment_id=comment_id, db=mock_db
            )
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
