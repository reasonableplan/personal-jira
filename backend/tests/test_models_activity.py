from app.models.activity import ActionType, Activity
from app.models.base import Base


class TestActionType:
    def test_values(self) -> None:
        assert ActionType.STATUS_CHANGE == "status_change"
        assert ActionType.COMMENT == "comment"
        assert ActionType.REVIEW_FEEDBACK == "review_feedback"
        assert ActionType.CODE_CHANGE == "code_change"


class TestActivityModel:
    def test_tablename(self) -> None:
        assert Activity.__tablename__ == "activities"

    def test_columns_exist(self) -> None:
        cols = {c.name for c in Activity.__table__.columns}
        assert cols == {"id", "task_id", "actor", "action_type", "content", "created_at"}

    def test_pk_is_uuid(self) -> None:
        col = Activity.__table__.c.id
        assert col.primary_key

    def test_task_id_fk(self) -> None:
        col = Activity.__table__.c.task_id
        fk = list(col.foreign_keys)[0]
        assert fk.target_fullname == "tasks.id"
        assert fk.ondelete == "CASCADE"

    def test_actor_not_nullable(self) -> None:
        assert Activity.__table__.c.actor.nullable is False

    def test_action_type_not_nullable(self) -> None:
        assert Activity.__table__.c.action_type.nullable is False

    def test_content_nullable(self) -> None:
        assert Activity.__table__.c.content.nullable is True

    def test_composite_index(self) -> None:
        idx_names = {idx.name for idx in Activity.__table__.indexes}
        assert "ix_activities_task_id_created_at" in idx_names

    def test_inherits_base(self) -> None:
        assert issubclass(Activity, Base)
