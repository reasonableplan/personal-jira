import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from personal_jira.models.issue import Issue, IssueStatus
from personal_jira.models.review import Review, ReviewDecision
from personal_jira.schemas.review import ReviewCreate, ReviewResponse
from personal_jira.services.review_service import ReviewService
from personal_jira.exceptions import (
    InvalidReviewTransitionError,
    IssueNotFoundError,
    IssueNotInReviewError,
)


class TestReviewDecisionEnum:
    def test_approved_value(self) -> None:
        assert ReviewDecision.APPROVED == "approved"

    def test_changes_requested_value(self) -> None:
        assert ReviewDecision.CHANGES_REQUESTED == "changes_requested"


class TestReviewModel:
    def test_create_review(self) -> None:
        issue_id = uuid.uuid4()
        review = Review(
            id=uuid.uuid4(),
            issue_id=issue_id,
            decision=ReviewDecision.APPROVED,
            comment="LGTM",
            reviewer="director",
            created_at=datetime.now(timezone.utc),
        )
        assert review.issue_id == issue_id
        assert review.decision == ReviewDecision.APPROVED
        assert review.comment == "LGTM"
        assert review.reviewer == "director"

    def test_review_defaults(self) -> None:
        review = Review(
            id=uuid.uuid4(),
            issue_id=uuid.uuid4(),
            decision=ReviewDecision.CHANGES_REQUESTED,
            reviewer="director",
            created_at=datetime.now(timezone.utc),
        )
        assert review.comment is None


class TestReviewSchema:
    def test_review_create_approved(self) -> None:
        schema = ReviewCreate(
            decision="approved",
            comment="Approved by director",
            reviewer="director",
        )
        assert schema.decision == ReviewDecision.APPROVED
        assert schema.comment == "Approved by director"

    def test_review_create_changes_requested(self) -> None:
        schema = ReviewCreate(
            decision="changes_requested",
            comment="Fix error handling",
            reviewer="director",
        )
        assert schema.decision == ReviewDecision.CHANGES_REQUESTED

    def test_review_create_invalid_decision(self) -> None:
        with pytest.raises(ValueError):
            ReviewCreate(
                decision="invalid",
                comment="nope",
                reviewer="director",
            )

    def test_review_create_without_comment(self) -> None:
        schema = ReviewCreate(decision="approved", reviewer="director")
        assert schema.comment is None

    def test_review_response_fields(self) -> None:
        review_id = uuid.uuid4()
        issue_id = uuid.uuid4()
        now = datetime.now(timezone.utc)
        resp = ReviewResponse(
            id=review_id,
            issue_id=issue_id,
            decision="approved",
            comment="good",
            reviewer="director",
            created_at=now,
            resulting_status=IssueStatus.DONE,
        )
        assert resp.id == review_id
        assert resp.resulting_status == IssueStatus.DONE


class TestReviewService:
    @pytest.fixture
    def mock_db(self) -> MagicMock:
        db = MagicMock()
        db.commit = MagicMock()
        db.add = MagicMock()
        db.refresh = MagicMock()
        return db

    @pytest.fixture
    def service(self) -> ReviewService:
        return ReviewService()

    def _make_issue(
        self,
        issue_id: uuid.UUID | None = None,
        status: IssueStatus = IssueStatus.IN_REVIEW,
    ) -> Issue:
        return Issue(
            id=issue_id or uuid.uuid4(),
            title="Test issue",
            status=status,
            priority="medium",
            issue_type="task",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

    def test_submit_review_approved_transitions_to_done(
        self, service: ReviewService, mock_db: MagicMock
    ) -> None:
        issue = self._make_issue()
        review_data = ReviewCreate(
            decision="approved", comment="Ship it", reviewer="director"
        )

        with patch.object(
            service, "_get_issue", return_value=issue
        ):
            result = service.submit_review(mock_db, issue.id, review_data)

        assert issue.status == IssueStatus.DONE
        assert result.decision == ReviewDecision.APPROVED
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()

    def test_submit_review_changes_requested_transitions_to_in_progress(
        self, service: ReviewService, mock_db: MagicMock
    ) -> None:
        issue = self._make_issue()
        review_data = ReviewCreate(
            decision="changes_requested",
            comment="Fix tests",
            reviewer="director",
        )

        with patch.object(
            service, "_get_issue", return_value=issue
        ):
            result = service.submit_review(mock_db, issue.id, review_data)

        assert issue.status == IssueStatus.IN_PROGRESS
        assert result.decision == ReviewDecision.CHANGES_REQUESTED

    def test_submit_review_issue_not_found(
        self, service: ReviewService, mock_db: MagicMock
    ) -> None:
        review_data = ReviewCreate(
            decision="approved", reviewer="director"
        )

        with patch.object(
            service, "_get_issue", return_value=None
        ):
            with pytest.raises(IssueNotFoundError):
                service.submit_review(mock_db, uuid.uuid4(), review_data)

    def test_submit_review_issue_not_in_review_status(
        self, service: ReviewService, mock_db: MagicMock
    ) -> None:
        issue = self._make_issue(status=IssueStatus.BACKLOG)
        review_data = ReviewCreate(
            decision="approved", reviewer="director"
        )

        with patch.object(
            service, "_get_issue", return_value=issue
        ):
            with pytest.raises(IssueNotInReviewError):
                service.submit_review(mock_db, issue.id, review_data)

    def test_submit_review_issue_in_progress_rejected(
        self, service: ReviewService, mock_db: MagicMock
    ) -> None:
        issue = self._make_issue(status=IssueStatus.IN_PROGRESS)
        review_data = ReviewCreate(
            decision="changes_requested", reviewer="director"
        )

        with patch.object(
            service, "_get_issue", return_value=issue
        ):
            with pytest.raises(IssueNotInReviewError):
                service.submit_review(mock_db, issue.id, review_data)

    def test_get_reviews_for_issue(
        self, service: ReviewService, mock_db: MagicMock
    ) -> None:
        issue_id = uuid.uuid4()
        mock_reviews = [
            Review(
                id=uuid.uuid4(),
                issue_id=issue_id,
                decision=ReviewDecision.CHANGES_REQUESTED,
                comment="Fix it",
                reviewer="director",
                created_at=datetime.now(timezone.utc),
            ),
            Review(
                id=uuid.uuid4(),
                issue_id=issue_id,
                decision=ReviewDecision.APPROVED,
                comment="Good now",
                reviewer="director",
                created_at=datetime.now(timezone.utc),
            ),
        ]
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = mock_reviews
        mock_db.query.return_value = mock_query

        results = service.get_reviews(mock_db, issue_id)
        assert len(results) == 2
        assert results[0].decision == ReviewDecision.CHANGES_REQUESTED
        assert results[1].decision == ReviewDecision.APPROVED


class TestReviewAPI:
    @pytest.fixture
    def mock_db(self) -> MagicMock:
        db = MagicMock()
        return db

    @pytest.fixture
    def client(self, mock_db: MagicMock) -> TestClient:
        from personal_jira.app import create_app
        from personal_jira.database import get_db

        app = create_app()
        app.dependency_overrides[get_db] = lambda: mock_db
        return TestClient(app)

    def test_post_review_approved_returns_200(
        self, client: TestClient, mock_db: MagicMock
    ) -> None:
        issue_id = uuid.uuid4()
        review_id = uuid.uuid4()
        now = datetime.now(timezone.utc)

        mock_review = Review(
            id=review_id,
            issue_id=issue_id,
            decision=ReviewDecision.APPROVED,
            comment="LGTM",
            reviewer="director",
            created_at=now,
        )

        with patch(
            "personal_jira.api.v1.endpoints.review.review_service.submit_review",
            return_value=mock_review,
        ) as mock_submit:
            response = client.post(
                f"/api/v1/issues/{issue_id}/review",
                json={
                    "decision": "approved",
                    "comment": "LGTM",
                    "reviewer": "director",
                },
            )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["decision"] == "approved"
        assert data["resulting_status"] == "done"

    def test_post_review_changes_requested_returns_200(
        self, client: TestClient, mock_db: MagicMock
    ) -> None:
        issue_id = uuid.uuid4()
        review_id = uuid.uuid4()
        now = datetime.now(timezone.utc)

        mock_review = Review(
            id=review_id,
            issue_id=issue_id,
            decision=ReviewDecision.CHANGES_REQUESTED,
            comment="Fix tests",
            reviewer="director",
            created_at=now,
        )

        with patch(
            "personal_jira.api.v1.endpoints.review.review_service.submit_review",
            return_value=mock_review,
        ):
            response = client.post(
                f"/api/v1/issues/{issue_id}/review",
                json={
                    "decision": "changes_requested",
                    "comment": "Fix tests",
                    "reviewer": "director",
                },
            )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["decision"] == "changes_requested"
        assert data["resulting_status"] == "in_progress"

    def test_post_review_issue_not_found_returns_404(
        self, client: TestClient, mock_db: MagicMock
    ) -> None:
        issue_id = uuid.uuid4()

        with patch(
            "personal_jira.api.v1.endpoints.review.review_service.submit_review",
            side_effect=IssueNotFoundError(issue_id),
        ):
            response = client.post(
                f"/api/v1/issues/{issue_id}/review",
                json={"decision": "approved", "reviewer": "director"},
            )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_post_review_issue_not_in_review_returns_422(
        self, client: TestClient, mock_db: MagicMock
    ) -> None:
        issue_id = uuid.uuid4()

        with patch(
            "personal_jira.api.v1.endpoints.review.review_service.submit_review",
            side_effect=IssueNotInReviewError(issue_id, IssueStatus.BACKLOG),
        ):
            response = client.post(
                f"/api/v1/issues/{issue_id}/review",
                json={"decision": "approved", "reviewer": "director"},
            )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_post_review_invalid_decision_returns_422(
        self, client: TestClient, mock_db: MagicMock
    ) -> None:
        issue_id = uuid.uuid4()
        response = client.post(
            f"/api/v1/issues/{issue_id}/review",
            json={"decision": "maybe", "reviewer": "director"},
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_post_review_missing_reviewer_returns_422(
        self, client: TestClient, mock_db: MagicMock
    ) -> None:
        issue_id = uuid.uuid4()
        response = client.post(
            f"/api/v1/issues/{issue_id}/review",
            json={"decision": "approved"},
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_get_reviews_returns_list(
        self, client: TestClient, mock_db: MagicMock
    ) -> None:
        issue_id = uuid.uuid4()
        now = datetime.now(timezone.utc)
        mock_reviews = [
            Review(
                id=uuid.uuid4(),
                issue_id=issue_id,
                decision=ReviewDecision.APPROVED,
                comment="ok",
                reviewer="director",
                created_at=now,
            )
        ]

        with patch(
            "personal_jira.api.v1.endpoints.review.review_service.get_reviews",
            return_value=mock_reviews,
        ):
            response = client.get(f"/api/v1/issues/{issue_id}/reviews")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["decision"] == "approved"

    def test_post_review_invalid_uuid_returns_422(
        self, client: TestClient, mock_db: MagicMock
    ) -> None:
        response = client.post(
            "/api/v1/issues/not-a-uuid/review",
            json={"decision": "approved", "reviewer": "director"},
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
